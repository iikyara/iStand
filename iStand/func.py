from pyzbar.pyzbar import decode
import requests
import json
import inspect
import numpy as np
import time
import pigpio
#import cv2
import io
from PIL import Image
from iStand import db, config
from iStand.models import *
from iStand.config import *

'''
# Using opencv
def image_to_barcode(image):
    stream = image.stream
    img_array = np.asarray(bytearray(stream.read()), dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if img is None:
        return -1
    result = decode(img)
    if len(result) == 0:
        return -1
    else:
        return [x[0].decode('utf-8', 'ignore') for x in result]
'''

# Using io and pillow
def image_to_barcode(image):
    img_read = image.stream.read()
    img_bin = io.BytesIO(img_read)
    img = Image.open(img_bin)
    if img is None:
        return -1
    result = decode(img)
    if len(result) == 0:
        return -1
    else:
        return [x[0].decode('utf-8', 'ignore') for x in result]

class BookInfo:
    def __init__(self,
        title,
        authors,
        isbn,
        publisher = '',
        detail = '',
        measure = (0, 0, 0),
        collection = '',
        thumbnail='',
        smallthumbail='',
        book_id=-1
    ):
        self.title = title
        self.authors = authors
        self.isbn = isbn
        self.publisher = publisher
        self.detail = detail
        self.measure = measure  #w x h x d
        self.collection = collection
        self.thumbnail = thumbnail
        self.smallthumbnail = smallthumbail
        self.book_id = book_id

    def __str__(self):
        return '<BookInfo title={!r} authors={!r} isbn={!r} publisher={!r} detail={!r} collection={!r} thumbnail={!r} smallthumbnail={!r}>'.format(self.title, self.authors, self.isbn, self.publisher, self.detail, self.collection, self.thumbnail, self.smallthumbnail)

    def to_json(self):
        return self.__dict__

def isbn_to_info_as_json(isbns):
    infos = isbn_to_info(isbns)
    list = []
    for info in infos:
        list.append(info.to_json())
    return list

def bookid_to_info_as_json(bookids):
    infos = bookid_to_info(bookids)
    list = []
    for info in infos:
        list.append(info.to_json())
    return list

#全てのisbnに対して本情報を検索する．
def isbn_to_info(isbns):
    list = []
    for isbn in isbns:
        list += isbn_to_info_from_opendb(isbn)
    return list

#全てのbookidに対して本情報を検索する．
def bookid_to_info(bookids):
    list = []
    for bookid in bookids:
        #bookidからisbnを取得
        print(bookid)
        isbn = db.session.query(Book.isbn).filter(Book.id==bookid).first()
        print(isbn)
        if isbn is None:
            continue
        isbn = isbn[0]
        list += isbn_to_info_from_opendb(isbn)
    return list

#openDBで本情報を検索
def isbn_to_info_from_opendb(isbn):
    #GETを作成
    get = {
        'isbn' : str(isbn),
    }
    #APIURL
    query = "https://api.openbd.jp/v1/get"
    info_str = requests.get(query, params=get).text
    info = json.loads(info_str)

    #取得したデータを解析
    #以下のURLのフォーマットを信じて実装
    #ONIXデータ仕様書
    #https://jpro2.jpo.or.jp/documents/%E5%87%BA%E7%89%88%E6%83%85%E5%A0%B1%E7%99%BB%E9%8C%B2%E3%82%BB%E3%83%B3%E3%82%BF%E3%83%BC%E3%80%8CONIX%E3%83%87%E3%83%BC%E3%82%BF%E4%BB%95%E6%A7%98%E7%AC%AC4%E7%89%88%EF%BC%88%E3%83%95%E3%82%A7%E3%83%BC%E3%82%BA2%EF%BC%89%E3%80%8D20180817.xlsx
    bookinfos = []
    for data in info:
        # 情報なしの時にはNoneが入ってくる
        if data is None:
            break

        detail = OnixToDetail(data['onix'])

        bookinfos.append(
            BookInfo(
                title           = APIParse(data, ['summary', 'title'], default="[ERROR:取得失敗]")[1],
                authors         = APIParse(data, ['summary', 'author'], default="情報なし")[1],
                isbn            = isbn,
                publisher       = APIParse(data, ['summary', 'publisher'], default="情報なし")[1],
                detail          = detail,
                thumbnail       = APIParse(data, ['summary', 'cover'], default="")[1],
                smallthumbail   = APIParse(data, ['summary', 'cover'], default="")[1]
            )
        )
    #for bi in bookinfos:
        #print(bi)
    return bookinfos

#detailは複数個含まれているため，選択する
def OnixToDetail(onix):
    #リストの順番は優先順位（左から優先順位の高い順に並べる．）
    TextTypes = ['03', '02', '23', '04']
    ContentAudience = ['00']
    #ContentAudience = ['00', '04'] #図書館員用情報を含めるバージョン（基本使わなくて良い）

    #CollateralDetailのTextContentの中に詳細が入っている
    isSuc, details = APIParse(onix, ['CollateralDetail', 'TextContent'], default=[])
    detail = "情報なし"
    if isSuc:
        for t in TextTypes:
            for c in ContentAudience:
                for d in details:
                    suc1, type = APIParse(d, ['TextType'])
                    suc2, audi = APIParse(d, ['ContentAudience'])
                    suc3, det  = APIParse(d, ['Text'])
                    #パース失敗（不正なデータ）
                    if not suc1 or not suc2 or not suc3:
                        continue
                    if t in type and c in audi:
                        detail = det
                        break
    return detail

def APIParse(json, query=[], default=""):
    isSuccess = True
    object = json
    for q in query:
        if type(object) is dict:
            if q in object:
                object = object[q]
            else:
                object = default
                isSuccess = False
                break
        elif type(object) is list:
            if type(q) is not int:
                object = defualt
                isSuccess = False
                break
            if 0 <= q < len(object):
                object = object[q]
            else:
                object = default
                isSuccess = False
                break
        else:
            break

    return isSuccess, object

#データベースに本を登録する
def add_book_to_db(data):
    try:
        book = Book(
            title = data['title'],
            isbn = data['isbn'],
            publisher = data['publisher'],
            thumbnail = data['thumbnail'],
            is_stored = False,
            block_id = -1
        )
    except Exception as e:
        print(e)
        return None
    db.session.add(book)
    db.session.commit()
    #print(book)
    try:
        author = Author(
            book_id = book.id,
            author = data['authors']
        )
    except Exception as e:
        print(e)
        return None
    db.session.add(author)
    db.session.commit()
    return book

#本を収納
def store_book_to_db(bookid, blockid):
    book = db.session.query(Book).filter(Book.id==bookid).first()
    if book is None:
        return False
    book.blockid = blockid
    book.is_stored = True
    db.session.commit()
    return True

#本の収納を取り消し（本の取り出し）
def pickup_book_from_db(bookid):
    book = db.session.query(Book).filter(Book.id==bookid).first()
    if book is None:
        return False
    book.is_stored = False
    db.session.commit()
    return True

def get_list_of_books(filter):
    list = []
    for book in db.session.query(Book).filter(Book.is_stored==filter['isStored']).all():
        authors = ["情報なし"]
        if len(book.author) != 0:
            authors = [x.author for x in book.author]
        list.append(
            BookInfo(
                title=book.title,
                authors=authors,
                isbn=book.isbn,
                publisher=book.publisher,
                thumbnail=book.thumbnail,
                smallthumbail=book.thumbnail,
                book_id = book.id
            )
        )
    return list

# 本取り出し（ブロックを検索して，ブロックが前面に来るように動く）
def pickup_book(bookid):
    blockid = get_blockid_from_bookid(bookid)
    print(blockid)
    moving_block_and_sonic_sensor(blockid)

def get_blockid_from_bookid(bookid):
    book = db.session.query(Book.block_id).filter(Book.id==bookid).first()
    if book is None:
        return -1
    return book[0]

# ブロック移動からセンサ感知までの一連の動作
isCompletedBlock = False
isCompletedSonicSensor = False
isFinished = False
def moving_block_and_sonic_sensor(blk):
    global isCompletedBlock
    global isCompletedSonicSensor
    global isFinished

    isCompletedBlock = False
    isCompletedSonicSensor = False
    isFinished = False
    print('initialize')

    start_moving_block(blk)
    isCompletedBlock = True
    print('Moving block is Completed.')

    isCompletedSonicSensor = catch_through_book([blk], 5)
    isFinished = True

    print('All is Finished.')

def get_state():
    return [isCompletedBlock, isCompletedSonicSensor, isFinished]

# ブロック移動
#isMovingBlock = False
# blk : ブロック番号
# blkで指定したブロックが前面に来るまで回す
def start_moving_block(blk):
    #isMovingBlock = True
    #処理
    #time.sleep(3)

    #pigpioチェック
    if not pigpio.pi().connected:
        return;

    block = db.session.query(Block.position).filter(Block.id==blk).first()
    if block is None:
        return;

    position = block[0]
    if position in [0, 1]:
        for i in range(4):
            rotate_motor(190, cw=True)
            rotate_motor(0, cw=False, isSW=True,
             pin_sw=config['PIN_SWITCHES_BOX'][(i + 2) % 4])

# cw = True で時計回り
def rotate_motor(rect, cw=True, isSW=False, pin_sw=-1):
    #pigpioに接続
    pi = pigpio.pi()

    # 接続チェック
    if not pi.connected:
        print('pigpio is not connected.')
        return;

    pi.set_mode(PIN_MOTOR1, pigpio.OUTPUT)
    pi.set_mode(PIN_MOTOR2, pigpio.OUTPUT)
    if isSW:
        pi.set_mode(pin_sw, pigpio.INPUT)

    pi.hardware_PWM(PIN_MOTOR1, MOTOR_FREQUENCY, MOTOR_DUTY if cw else 0)
    pi.hardware_PWM(PIN_MOTOR2, MOTOR_FREQUENCY, MOTOR_DUTY if not cw else 0)

    # 調整
    if isSW:
        while pi.read(pin_sw) == 1:
            pass
    else:
        time.sleep(rect / config['MOTOR_SPEED'])

    pi.hardware_PWM(PIN_MOTOR1, MOTOR_FREQUENCY, 0)
    pi.hardware_PWM(PIN_MOTOR2, MOTOR_FREQUENCY, 0)

    pi.set_mode(PIN_MOTOR1, pigpio.INPUT)
    pi.set_mode(PIN_MOTOR2, pigpio.INPUT)
    pi.stop()

'''
def is_moving_block():
    return isMovingBlock
'''

# 超音波センサー
isRunningSonicSensor = False
terminationSonicSensorRequest = False
stateOfSonicSensor1 = -1 #距離を格納
stateOfSonicSensor2 = -1 #距離を格納
def start_sonic_sensor():
    global isRunningSonicSensor
    global terminationSonicSensorRequest
    global stateOfSonicSensor1
    global stateOfSonicSensor2

    #既に稼働済みなら実行しない
    if isRunningSonicSensor:
        return

    isRunningSonicSensor = True

    # pigpioに接続
    pi = pigpio.pi()

    # 接続チェック
    if not pi.connected:
        print('pigpio is not connected.')
        return;

    pi.set_mode(config["PIN_SONICSENSOR1_ECHO"], pigpio.INPUT)
    pi.set_mode(config["PIN_SONICSENSOR1_TRIG"], pigpio.OUTPUT)
    pi.set_mode(config["PIN_SONICSENSOR2_ECHO"], pigpio.INPUT)
    pi.set_mode(config["PIN_SONICSENSOR2_TRIG"], pigpio.OUTPUT)

    # 超音波センサーで距離を測定
    terminationSonicSensorRequest = False
    while not terminationSonicSensorRequest:
        pass

    pi.set_mode(config["PIN_SONICSENSOR1_ECHO"], pigpio.INPUT)
    pi.set_mode(config["PIN_SONICSENSOR1_TRIG"], pigpio.INPUT)
    pi.set_mode(config["PIN_SONICSENSOR2_ECHO"], pigpio.INPUT)
    pi.set_mode(config["PIN_SONICSENSOR2_TRIG"], pigpio.INPUT)
    pi.stop()

    isRunningSonicSensor = False

def stop_sonic_sensor():
    global isRunningSonicSensor
    global terminationSonicSensorRequest
    # 終了リクエスト
    terminationSonicSensorRequest = True
    #終了確認
    cnt = 0
    # 3秒以内に停止しなかったらエラー
    while isRunningSonicSensor:
        time.sleep(0.1)
        cnt += 1
        if cnt > 30:
            return False
    return True

# n秒間本の通過の感知を試みる
# blksはブロック番号のリスト．以下で指定
# 2 4
# 1 3
UPPER_CENTER = 22.5
LOWER_CENTER = 7.5
BLOCK_RANGE = 15
def catch_through_book(blks, n):
    global isRunningSonicSensor

    #既に稼働済みなら実行しない
    if isRunningSonicSensor:
        print('duplication')
        return False

    isRunningSonicSensor = True

    PIN = [
        {
            'ECHO': config["PIN_SONICSENSOR1_ECHO"],
            'TRIG': config["PIN_SONICSENSOR1_TRIG"]
        },
        {
            'ECHO': config["PIN_SONICSENSOR2_ECHO"],
            'TRIG': config["PIN_SONICSENSOR2_TRIG"]
        }
    ]

    pi = pigpio.pi()

    # 接続チェック
    if not pi.connected:
        print('pigpio is not connected.')
        return False;

    pi.set_mode(PIN[0]['ECHO'], pigpio.INPUT)
    pi.set_mode(PIN[0]['TRIG'], pigpio.OUTPUT)
    pi.set_mode(PIN[1]['ECHO'], pigpio.INPUT)
    pi.set_mode(PIN[1]['TRIG'], pigpio.OUTPUT)

    # 1秒間に10回
    for _ in range(n * 10):
        result = [0, 0]
        for i in range(2):
            pi.write(PIN[i]['TRIG'], 0)

            time.sleep(0.3)
            # send a 10us plus to Trigger
            pi.write(PIN[i]['TRIG'], 1)
            time.sleep(0.00001)
            pi.write(PIN[i]['TRIG'], 0)

            # detect TTL level signal on Echo
            while pi.read(PIN[i]['ECHO']) == 0:
              signaloff = time.time()
            while pi.read(PIN[i]['ECHO']) == 1:
              signalon = time.time()

            # calculate the time interval
            timepassed = signalon - signaloff

            # we now have our distance but it's not in a useful unit of
            # measurement. So now we convert this distance into centimetres
            result[i] = timepassed * (331.50 + 0.606681 * 20)* 100/2

        # 判別
        for blk in blks:
            if blk == 1 and (LOWER_CENTER - BLOCK_RANGE) <= result[0] <= (LOWER_CENTER + BLOCK_RANGE):
                return True
            elif blk == 2 and (UPPER_CENTER - BLOCK_RANGE) <= result[0] <= (UPPER_CENTER + BLOCK_RANGE):
                return True
            elif blk == 3 and (LOWER_CENTER - BLOCK_RANGE) <= result[1] <= (LOWER_CENTER + BLOCK_RANGE):
                return True
            elif blk == 4 and (UPPER_CENTER - BLOCK_RANGE) <= result[1] <= (UPPER_CENTER + BLOCK_RANGE):
                return True

        time.sleep(0.1)

    pi.set_mode(PIN[0]['EHCO'], pigpio.INPUT)
    pi.set_mode(PIN[0]['TRIG'], pigpio.INPUT)
    pi.set_mode(PIN[1]['EHCO'], pigpio.INPUT)
    pi.set_mode(PIN[1]['TRIG'], pigpio.INPUT)
    pi.stop()

    isRunningSonicSensor = False
    return False

def get_state_of_sonic_sensor():
    return [stateOfSonicSensor1, stateOfSonicSensor2]

if __name__ == '__main__':
    #isbn_to_info_from_opendb(9784101006062)
    #isbn_to_info_from_opendb(1920082019006)
    #isbn_to_info_from_opendb(9784523172765)
    #isbn_to_info_from_opendb(9784088807232)
    #isbn_to_info_from_opendb(4088725093)
    #print(APIParse(data, ['summary', 'title'], default="title"))
    #print(APIParse(data, ['summary', 'titlee'], default="title"))
    #print(APIParse(data, ['onix', 'CollateralDetail', 'TextContent', 1, 'Text'], default="detail"))
    #infos = isbn_to_info_as_json(["9784101006062", "9784523172765", 1920082019006])
    #infos = bookid_to_info_as_json([0, 1])

    for bi in infos:
        print(bi)

from pyzbar.pyzbar import decode
import requests
import json
import inspect
import numpy as np
import cv2
from iStand import db
from iStand.models import *

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

#全てのisbnに対して本情報を検索する．
def isbn_to_info(isbns):
    list = []
    for isbn in isbns:
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
    db.session.add(author)
    db.session.commit()
    return True

def get_list_of_books():
    list = []
    for book in db.session.query(Book).all():
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

if __name__ == '__main__':
    #isbn_to_info_from_opendb(9784101006062)
    #isbn_to_info_from_opendb(1920082019006)
    #isbn_to_info_from_opendb(9784523172765)
    #isbn_to_info_from_opendb(9784088807232)
    #isbn_to_info_from_opendb(4088725093)
    #print(APIParse(data, ['summary', 'title'], default="title"))
    #print(APIParse(data, ['summary', 'titlee'], default="title"))
    #print(APIParse(data, ['onix', 'CollateralDetail', 'TextContent', 1, 'Text'], default="detail"))
    infos = isbn_to_info_as_json(["9784101006062", "9784523172765", 1920082019006])
    for bi in infos:
        print(bi)

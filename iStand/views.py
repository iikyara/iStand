import flask
from flask import render_template, redirect, jsonify, request
#import requests
from iStand import app
from iStand.models import *
from iStand.func import *
import threading

@app.route('/show_block/')
def show_blocks():
    disp = str([("BLOCK", x.id, x.position) for x in Block.query.all()])
    return disp

@app.route('/')
def show_home():
    return render_template('home.html')

@app.route('/management/')
def show_management():
    return render_template('management.html')

@app.route('/search/')
def return_search_result():
    filter = {
        "query" : "",
        "isStored" : True,
    }
    print(request.args.get("query"))
    if request.method == "GET":
        for f in filter.keys():
            if request.args.get(f):
                filter[f] = request.args.get(f)
                print(filter)
    #本情報の取得
    books = get_list_of_books(filter)
    result = []
    for book in books:
        result.append(
            render_template("parts_searchlist.html", book=book)
        )
    return jsonify({
        'success' : True,
        'data' : result
    })

@app.route('/additional/')
def show_additional():
    return render_template('additional.html')

@app.route('/addfromcam/')
def show_addfromcam():
    return render_template('addfromcam.html')

@app.route('/addfromisbn/')
def show_addfromisbn():
    return render_template('addfromisbn.html')

@app.route('/addfromhist/')
def show_addfromhist():
    return render_template('addfromhist.html')

@app.route('/confirm_pick/', methods=["POST"])
def show_confirm_pick():
    if request.method != 'POST':
        return redirect('/')
    return render_template('confirm.html')

@app.route('/confirm_add/', methods=["POST"])
def show_confirm_add():
    if request.method != 'POST':
        return redirect('/')
    data = {
        'title' : request.form["title"],
        'isbn' : request.form["isbn"],
        'authors' : request.form["authors"],
        'publisher' : request.form["publisher"],
        'thumbnail' : request.form["thumbnail"],
    }
    return render_template('confirm.html', data=data)

@app.route('/image_to_info_as_html/', methods=["POST"])
def return_image_to_info_as_html():
    if request.method != 'POST':
        return jsonify({'success' : False, 'message' : "only post request"})
    img_file = request.files['pic']
    # 画像チェック
    if not img_file:
        return jsonify({'success' : False, 'message' : "不正な画像"})
    # 画像からバーコードに変換
    barcodes = image_to_barcode(img_file)
    # バーコード取得チェック
    if barcodes == -1:
        return jsonify({'success' : False, 'message' : "バーコード取得失敗"})
    # apiから情報を取得
    books = isbn_to_info(barcodes)
    result = []
    for i in range(len(books)):
        result.append(
            render_template('parts_detail.html', number=i, book=books[i])
        )
    return jsonify({
        'success' : True,
        'data' : result
    })

@app.route('/isbn_to_info_as_html/', methods=["POST"])
def return_isbn_to_info_as_html():
    if request.method != 'POST':
        return jsonify({'success' : False, 'message' : "only post request"})
    json = request.json
    print(json)
    if 'isbns' in json:
        books = isbn_to_info_as_json(json['isbns'])
        result = []
        for i in range(len(books)):
            result.append(
                render_template('parts_detail.html', number=i, book=books[i])
            )
        return jsonify({
            'success' : True,
            'data' : result
        })
    else:
        return jsonify({'success' : False, 'message' : "request does not contain isbns."})

@app.route('/isbn_to_info/', methods=["POST"])
def return_isbn_to_info():
    if request.method != 'POST':
        return jsonify({'success' : False, 'message' : "only post request"})
    json = request.json
    if 'isbns' in json:
        return jsonify({
            'success' : True,
            'data' : isbn_to_info_as_json(json['isbns'])
        })
    else:
        return jsonify({'success' : False, 'message' : "request does not contain isbns."})

@app.route('/bookid_to_info_as_html/', methods=["POST"])
def return_bookid_to_info_as_html():
    if request.method != 'POST':
        return jsonify({'success' : False, 'message' : "only post request"})
    json = request.json
    if 'bookids' in json:
        books = bookid_to_info_as_json(json['bookids'])
        result = []
        for i in range(len(books)):
            result.append(
                render_template('parts_detail.html', number=i, book=books[i])
            )
        return jsonify({
            'success' : True,
            'data' : result
        })
    else:
        return jsonify({'success' : False, 'message' : "request does not contain isbns."})

@app.route('/pickup/', methods=["POST"])
def show_pickup():
    if request.method != 'POST':
        return jsonify({'success' : False, 'message' : "only post request"})
    data = request.form
    t = threading.Thread(target=pickup_book, args=([data['bookid']]))
    t.start()
    bookdata = bookid_to_info_as_json(data['bookid'])[0]
    blockid = get_blockid_from_bookid(data['bookid'])
    print("blockid", blockid)
    bookdata['block_id'] = blockid
    bookdata['operation'] = 'pickup'
    return render_template('complete.html', data=bookdata)

@app.route('/moving/', methods=["POST"])
def show_moving():
    if request.method != 'POST':
        return jsonify({'success' : False, 'message' : "only post request"})
    data = request.form
    t = threading.Thread(target=moving_block_and_sonic_sensor,
    args=([data['blockid']]))
    t.start()
    bookdata = {
        'title' : request.form["title"],
        'isbn' : request.form["isbn"],
        'authors' : request.form["authors"],
        'publisher' : request.form["publisher"],
        'thumbnail' : request.form["thumbnail"],
    }
    book = add_book_to_db(bookdata)
    bookdata['book_id'] = book.id
    bookdata['operation'] = 'add'
    return render_template('complete.html', data=bookdata)

@app.route('/update_book/', methods=["POST"])
def return_update_book():
    data = request.json
    result = False
    if data['operation'] == "add":
        result = store_book_to_db(data['book_id'], data['block_id'])
    elif data['operation'] == "pickup":
        result = pickup_book_from_db(data['book_id'])
    return jsonify({'success' : result})

@app.route('/get_state/')
def return_state():
    return jsonify({'success' : True, 'data' : get_state()})
'''
@app.route('/moving/', methods=["POST"])
def show_moving():
    if request.method != 'POST':
        return jsonify({'success' : False, 'message' : "only post request"})
    data = request.form
    start_moving_block(data['blockid'])
    return render_template('complete.html', data=data)
'''

@app.route('/is_moving_block/')
def return_is_moving_block():
    return jsonify({'success' : True, 'data' : is_moving_block()})

@app.route('/start_sonic_sensor/')
def return_start_sonic_sensor():
    t = threading.Thread(target=start_sonic_sensor)
    t.start()
    return jsonify({'success' : True, 'message' : "Sonic sensor is running."})

@app.route('/stop_sonic_sensor/')
def return_stop_sonic_sensor():
    result = stop_sonic_sensor()
    return jsonify({'success' : result, 'message' : "Sonic sensor is stopped." if result else "Error: Sonic sensor cannot stopped."})

@app.route('/state_of_sonic_sensor/')
def return_state_of_sonic_sensor():
    state = state_of_sonic_sensor()
    return jsonify({'success' : True, 'data' : state})

@app.route('/image_to_barcode/', methods=["POST"])
def return_image_to_barcode():
    if request.method != 'POST':
        return jsonify({'success' : False, 'message' : "only post request"})
    img_file = request.files['pic']
    if not img_file:
        return jsonify({'success' : False, 'message' : "不正な画像"})
    result = image_to_barcode(img_file)
    if result == -1:
        return jsonify({'success' : False, 'message' : "バーコード取得失敗"})
    return jsonify({'success' : True, 'data' : result})

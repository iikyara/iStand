import flask
from flask import render_template, redirect, jsonify, request
#import requests
from iStand import app
from iStand.models import *
from iStand.func import *

@app.route('/show_block/')
def show_blocks():
    disp = str([("BLOCK", x.id, x.position) for x in Block.query.all()])
    return disp

@app.route('/')
def show_home():
    return render_template('home.html')

@app.route('/management/')
def show_management():
    books = get_list_of_books()
    for book in books:
        print(book)
    return render_template('management.html')

@app.route('/search/')
def return_search_result():
    filter = {
        "query" : "",
        "isStored" : False,
    }
    if request.method == "GET":
        for f in filter.keys():
            if request.args.get(f):
                filter[f] = request.args.get(f)
                print(filter)
    #本情報の取得
    books = get_list_of_books()
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
    add_book_to_db(data)
    return render_template('confirm.html')

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
    json = request.get_json()
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
    json = request.get_json()
    if 'isbns' in json:
        return jsonify({
            'success' : True,
            'data' : isbn_to_info_as_json(json['isbns'])
        })
    else:
        return jsonify({'success' : False, 'message' : "request does not contain isbns."})

@app.route('/moving/')
def show_moving():
    return render_template('moving.html')

@app.route('/complete/')
def show_complete():
    return render_template('complete.html')

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

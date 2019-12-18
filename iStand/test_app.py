from flask import Flask, render_template, request, url_for
#import requests
from iStand import app
from pyzbar.pyzbar import decode
import inspect
import numpy as np
import cv2
import os

#app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/test')
def home():
    name = "Hoge"
    #return name
    return render_template('test_home.html', title='flask test', name=name) #変更

@app.route('/test_camera')
def test_camera():
    #return name
    return render_template('test_camera.html', title='camera test') #変更

@app.route('/test_barcode', methods=['POST'])
def test_barcode():
    if request.method == 'POST':
        img_file = request.files['pic']
        if img_file:
            result = image_to_barcode(img_file)
            if len(result) == -1:
                code = "Failure"
            else:
                code = result[0][0].decode('utf-8', 'ignore')
            return render_template('test_barcode.html', code=code)
    #return name
    return render_template('test_camera.html', title='barcode test') #変更

@app.route('/test_api', methods=['POST'])
def test_api():
    if request.method == 'POST':
        img_file = request.files['pic']
        if img_file:
            print('start decoding')
            result = image_to_barcode(img_file)
            print('end to decode')
            if len(result) == -1:
                info = "ISBN Failure"
            else:
                get = {
                    'operation' : 'searchRetrieve',
                    'query' : 'isbn=' + str(result),
                }
                query = "http://iss.ndl.go.jp/api/sru"
                #info = query
                info = requests.get(query, params=get).text
            print('end to get info')
            return render_template('test_api.html', info=info)
    return render_template('test_home.html', title='api test') #変更

@app.route('/test_bootstrap')
def view_bootstrap():
    return render_template("test_bootstrap.html")

def image_to_barcode(image):
    stream = image.stream
    img_array = np.asarray(bytearray(stream.read()), dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    result = decode(img)
    if len(result) == 0:
        code = -1
    else:
        code = result[0][0].decode('utf-8', 'ignore')
    return code

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)

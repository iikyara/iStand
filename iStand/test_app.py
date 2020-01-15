from flask import Flask, render_template, request, url_for, jsonify
#import requests
from iStand import app, config
from pyzbar.pyzbar import decode
import inspect
import numpy as np
#import cv2
import pigpio
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

@app.route('/test_confirm')
def view_confirm():
    title = "Test Bookテスト本"
    isbn = "0123456789012"
    authors = "地球にやさしいエコマーク"
    publisher = ""
    thumbnail = "https://akira-watson.com/wp-content/uploads/2019/07/cat45_01.jpg"
    data = {
        'title' : "Test Bookテスト本",
        'isbn' : "0123456789012",
        'authors' : "地球にやさしいエコマーク",
        'publisher' : "我らが地球",
        'thumbnail' : "https://akira-watson.com/wp-content/uploads/2019/07/cat45_01.jpg",
    }
    return render_template("confirm.html", data=data)

# モーターテスト
pi = pigpio.pi()
isMoving = False
frequency = 10000
dutycycle = 500000
@app.route('/test_motor')
def show_test_motor():
    return render_template("test_motor.html")

@app.route('/start_motor/', methods=["POST"])
def start_motor():
    print(request.json)
    data = request.json
    pin = -1
    if data['isRight']:
        pin = config['PIN_MOTOR1']
    else:
        pin = config['PIN_MOTOR2']

    # gpio set up
    pi.set_mode(pin, pigpio.OUTPUT)
    set_freq_and_duty(pin, freq = data['freq'], duty = data['duty'])

    return jsonify({'success' : True, 'message' : 'start motor'})

@app.route('/stop_motor/', methods=["POST"])
def stop_motor():
    print(request.json)
    data = request.json
    pin = -1
    if data['isRight']:
        pin = config['PIN_MOTOR1']
    else:
        pin = config['PIN_MOTOR2']
    set_freq_and_duty(pin, freq = data['freq'], duty = 0)
    return jsonify({'success' : True, 'message' : 'stop motor'})

@app.route('/set_freq_and_duty/', methods=["POST"])
def exe_set_freq_and_duty():
    data = request.json
    data = request.json
    pin = -1
    if data['isRight']:
        pin = config['PIN_MOTOR1']
    else:
        pin = config['PIN_MOTOR2']
    set_freq_and_duty(pin, freq = data['freq'], duty = data['duty'])
    return jsonify({'success' : True, 'message' : 'stop motor'})

def set_freq_and_duty(pin, freq = frequency, duty = dutycycle):
    global frequency
    global dutycycle
    frequency = freq
    dutycycle = duty
    pi.hardware_PWM(pin, freq, duty)

@app.route('/upload_motor_data/', methods=["POST"])
def upload_motor_data():
    data = request.json
    config['MOTOR_FREQUENCY'] = data['freq']
    config['MOTOR_DUTY'] = data['duty']
    config['MOTOR_SPEED'] = data['speed']
    motor_data = db.session.query(Motor).first()
    motor_data['frequency'] = data['freq']
    motor_data['dutycycle'] = data['duty']
    motor_data['speed'] = data['speed']
    db.session.commit()

def image_to_barcode(image):
    stream = image.stream
    img_array = np.asarray(bytearray(stream.read()), dtype=np.uint8)
    #img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    img = None
    result = decode(img)
    if len(result) == 0:
        code = -1
    else:
        code = result[0][0].decode('utf-8', 'ignore')
    return code

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)

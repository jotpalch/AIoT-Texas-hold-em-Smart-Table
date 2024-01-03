import datetime
import os
import pathlib
import filetype
from flask import Flask, flash, request, redirect, url_for, render_template
from flask_cors import CORS
import time
import threading
import torch
import json
import random

import poker_multiprocess

# 取得目前檔案所在的資料夾
SRC_PATH = pathlib.Path(__file__).parent.absolute()
UPLOAD_FOLDER = os.path.join(SRC_PATH, 'static', 'uploads')

app = Flask(__name__)
CORS(app)
app.secret_key = b'_qweqwrwqrtyuiqwe'     # change secret key
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

i = 0
model = torch.hub.load('../yolov5', 'custom', path='./static/model/best.pt', source='local')
mapping = ['TH', 'TS', 'TC', '2D', '2H', '2S', '2C', '3D', '3H', '3S', '3C', '4D', '4H', '4S', '4C', '5D', '5H', '5S', '5C', 'xxxx', 'TD', '6D', '6H', '6S', '6C', '7D', '7H', '7S', '7C', '8D', '8H', '8S', '8C', '9D', '9H', '9S', '9C', 'AD', 'AH', 'AS', 'AC', 'JD', 'JH', 'JS', 'JC', 'KD', 'KH', 'KS', 'KC', 'QD', 'QH', 'QS', 'QC']

prelist = ["AS", "AC"]
rate = ["-", "-", "-"]

prelist_duo = [ ["AS", "AC"], ["AH", "AD"] ]
rate_duo = [ ["-", "-", "-"], ["-", "-", "-"] ]


def predict(filename):
    global prelist
    global rate
    try:
        im = './static/uploads/' + filename

        results = model(im)
        df = results.pandas().xyxy[0]['class']
        pre = df.values
        if len(pre) >= 2:
            prelist = [mapping[i] for i in pre[:2]]
            Simulation = poker.MonteCarlo()

            PlayerAmount = 2
            my_hands = { (card[0], card[1]) for card in prelist }
            op_hands = {}
            current_table_cards = {}

            Simulation_multiprocess = poker_multiprocess.MonteCarlo_multiprocess()
            Simulation_multiprocess.Run(my_hands, op_hands, current_table_cards, PlayerAmount, 200000, 20)
            rate = Simulation_multiprocess.GetRate()

    except:
        prelist = ["AS", "AS"]
        rate = ["-", "-", "-"]

    print(prelist, rate)

def predict_duo(filename):
    global prelist_duo
    global rate_duo
    try:
        im = './static/uploads/' + filename

        results = model(im)
        df = results.pandas().xyxy[0]['class']
        pre = df.values
        if len(pre) >= 2:
            prelist_duo = [ prelist, [mapping[i] for i in pre[:2]] ]

            PlayerAmount = 2
            my_hands = { (card[0], card[1]) for card in prelist_duo[0] }
            op_hands = { (card[0], card[1]) for card in prelist_duo[1] }
            current_table_cards = {}

            Simulation_multiprocess = poker_multiprocess.MonteCarlo_multiprocess()
            Simulation_multiprocess.Run(my_hands, op_hands, current_table_cards, PlayerAmount, 200000, 20)
            rate_duo[0] = Simulation_multiprocess.GetRate()

            Simulation_multiprocess = poker_multiprocess.MonteCarlo_multiprocess()
            Simulation_multiprocess.Run(op_hands, my_hands, current_table_cards, PlayerAmount, 200000, 20)
            rate_duo[1] = Simulation_multiprocess.GetRate()

    except:
        prelist_duo = [ ["AS", "AC"], ["AH", "AD"] ]
        rate_duo = [ ["-", "-", "-"], ["-", "-", "-"] ]

    print(prelist_duo, rate_duo)

@app.route('/')
def index():
    return render_template('index.html', prelist=prelist, rate=rate)

@app.route('/show')
def show():
    pic = []
    pic = random.sample([i for i in mapping if i != "xxxx"], k=2)

    return render_template('show.html', pic=pic)

@app.route('/getinfo', methods=['POST', 'GET'])
def getinfo():
    data = {
        "prelist": prelist,
        "rate": rate
    }
    return json.dumps(data)

@app.route('/', methods=['POST'])
def upload_file():
    res = handle_file(request)

    if res['msg'] == 'ok':
        flash('影像上傳完畢！')
        return render_template('index.html', filename=res['filename'])
    elif res['msg'] == 'type_error':
        flash('僅允許上傳png, jpg, jpeg和gif影像檔')
    elif res['msg'] == 'empty':
        flash('請選擇要上傳的影像')
    elif res['msg'] == 'no_file':
        flash('沒有上傳檔案')

    return redirect(url_for('index'))  # 令瀏覽器跳回首頁


@app.route('/esp32cam', methods=['POST'])
def esp32cam():
    res = handle_file(request)
    if res.get("filename") != None:
        predict(res.get("filename"))
    return res['msg']

@app.route('/esp32cam_op', methods=['POST'])
def esp32cam_op():
    res = handle_file(request)
    if res.get("filename") != None:
        predict_duo(res.get("filename"))
    return res['msg']

def handle_file(request):
    if 'filename' not in request.files:
        return {"msg": 'no_file'}  # 傳回代表「沒有檔案」的訊息

    file = request.files['filename']  # 取得上傳檔

    if file.filename == '':
        return {"msg": 'empty'}       # 傳回代表「空白」的訊息

    if file:
        file_type = filetype.guess_extension(file)  # 判斷上傳檔的類型

        if file_type in ALLOWED_EXTENSIONS:
            file.stream.seek(0)
            # filename = secure_filename(file.filename)
            # 重新設定檔名：日期時間 + ‘.’ + ‘副檔名’
            # filename = str(datetime.datetime.now()).replace(':', '_') + '.' + file_type
            global i
            filename = f"pic_{i}" + '.' + file_type
            i += 1
            file.save(os.path.join(
                app.config['UPLOAD_FOLDER'], filename))
            # 傳回代表上傳成功的訊息以及檔名。
            return {"msg": 'ok', "filename": filename}
        else:
            return {"msg": 'type_error'}  # 傳回代表「檔案類型錯誤」的訊息


@app.route('/img/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=38999)
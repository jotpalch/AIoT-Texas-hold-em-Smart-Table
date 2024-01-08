import os
import pathlib
import filetype
from flask import Flask, request, redirect, url_for, render_template
from flask_cors import CORS
import torch
import json
import random
import requests

import poker_multiprocess

# 取得目前檔案所在的資料夾
SRC_PATH = pathlib.Path(__file__).parent.absolute()
UPLOAD_FOLDER = os.path.join(SRC_PATH, 'static', 'uploads')

app = Flask(__name__)
CORS(app)
app.secret_key = b'_qweqwrwqrtyuiqwe'     # change secret key
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024

line_token = "aaaaaaaaaaaaaaa" # change line token

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

i = 0
model = torch.hub.load('../yolov5', 'custom', path='./static/model/best.pt', source='local')
mapping = ['TH', 'TS', 'TC', '2D', '2H', '2S', '2C', '3D', '3H', '3S', '3C', '4D', '4H', '4S', '4C', '5D', '5H', '5S', '5C', 'xxxx', 'TD', '6D', '6H', '6S', '6C', '7D', '7H', '7S', '7C', '8D', '8H', '8S', '8C', '9D', '9H', '9S', '9C', 'AD', 'AH', 'AS', 'AC', 'JD', 'JH', 'JS', 'JC', 'KD', 'KH', 'KS', 'KC', 'QD', 'QH', 'QS', 'QC']

prelist = ["card", "card"]
notifylist = ["card", "card"]
rate = ["-", "-", "-"]

prelist_duo = [ ["card", "card"], ["card", "card"] ]
rate_duo = [ ["-", "-", "-"], ["-", "-", "-"] ]
tablelist = ["card", "card", "card", "card", "card"]

is_game_start = 0

def notify(msg, li):
    global notifylist
    url = 'https://notify-api.line.me/api/notify'
    headers = {
        'Authorization': 'Bearer ' + line_token 
    }
    data = {
        'message': msg
    }
    if notifylist != li :
        data = requests.post(url, headers=headers, data=data) 
        notifylist = li

def predict(filename):
    global prelist
    global rate
    global is_game_start
    try:
        if is_game_start :
            return

        im = './static/uploads/' + filename

        results = model(im)
        df = results.pandas().xyxy[0]['class']
        pre = df.values
        if len(pre) >= 2:
            prelist = [mapping[i] for i in pre[:2]]

            PlayerAmount = 2
            my_hands = { (card[0], card[1]) for card in prelist }
            op_hands = {}
            current_table_cards = {}

            Simulation_multiprocess = poker_multiprocess.MonteCarlo_multiprocess()
            Simulation_multiprocess.Run(my_hands, op_hands, current_table_cards, PlayerAmount, 200000, 20)
            rate = Simulation_multiprocess.GetRate()

            notify(f"\nWin Rate: {rate[0]}", prelist)

    except:
        prelist = ["card", "card"]
        rate = ["-", "-", "-"]

    print(prelist, rate)

def predict_duo(filename):
    global prelist_duo
    global rate_duo
    global is_game_start
    try:
        if is_game_start :
            return

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
        prelist_duo = [ ["card", "card"], ["card", "card"] ]
        rate_duo = [ ["-", "-", "-"], ["-", "-", "-"] ]

    print(prelist_duo, rate_duo)

def predict_table(filename):
    global prelist_duo
    global rate_duo
    global tablelist
    global is_game_start
    try:
        im = './static/uploads/' + filename

        results = model(im)
        df = results.pandas().xyxy[0]['class']
        pre = df.values

        if len(pre) < 2:
            if tablelist.count("card") == 0 and is_game_start >= 3:
                prelist_duo = [ ["card", "card"], ["card", "card"] ]
                rate_duo = [ ["-", "-", "-"], ["-", "-", "-"] ]

            is_game_start = 0
            tablelist = ["card", "card", "card", "card", "card"]

            return

        if tablelist.count("card") == 5 and len(pre) >= 3 :
            tablelist[:3] = [mapping[i] for i in pre[:3]]

        elif tablelist.count("card") == 2 and len(pre) >= 4 :
            tablelist[:4] = [mapping[i] for i in pre[:4]]

        elif tablelist.count("card") == 1 and len(pre) >= 5 :
            tablelist = [mapping[i] for i in pre[:5]]
        
        else :
            return
        
        is_game_start += 1

        PlayerAmount = 2
        my_hands = { (card[0], card[1]) for card in prelist_duo[0] }
        op_hands = { (card[0], card[1]) for card in prelist_duo[1] }
        current_table_cards = { (card[0], card[1]) for card in tablelist if card != "card" }

        Simulation_multiprocess = poker_multiprocess.MonteCarlo_multiprocess()
        Simulation_multiprocess.Run(my_hands, op_hands, current_table_cards, PlayerAmount, 200000, 20)
        rate_duo[0] = Simulation_multiprocess.GetRate()

        Simulation_multiprocess = poker_multiprocess.MonteCarlo_multiprocess()
        Simulation_multiprocess.Run(op_hands, my_hands, current_table_cards, PlayerAmount, 200000, 20)
        rate_duo[1] = Simulation_multiprocess.GetRate()

    except:
        tablelist = ["card", "card", "card", "card", "card"]

    print(prelist_duo, rate_duo, tablelist)

@app.route('/')
def index():
    return render_template('index.html', prelist=prelist, rate=rate)

@app.route('/live')
def live():
    return render_template('live.html', prelist_duo=prelist_duo, rate_duo=rate_duo, tablelist=tablelist)

@app.route('/show')
def show():
    pic = []
    pic = random.sample([i for i in mapping if i != "xxxx"], k=2)

    return render_template('show.html', pic=pic)

@app.route('/pic')
def pic():
    return render_template('pic.html')

@app.route('/getinfo', methods=['POST', 'GET'])
def getinfo():
    data = {
        "prelist": prelist,
        "rate": rate
    }
    return json.dumps(data)

@app.route('/getinfo_live', methods=['POST', 'GET'])
def getinfo_live():
    data = {
        "prelist_duo": prelist_duo,
        "rate_duo": rate_duo,
        "tablelist": tablelist,
        "is_game_start": is_game_start
    }
    return json.dumps(data)

@app.route('/esp32cam', methods=['POST'])
def esp32cam():
    res = handle_file(request, "my")
    if res.get("filename") != None:
        predict(res.get("filename"))
    return res['msg']

@app.route('/esp32cam_op', methods=['POST'])
def esp32cam_op():
    res = handle_file(request, "op")
    if res.get("filename") != None:
        predict_duo(res.get("filename"))
    return res['msg']

@app.route('/table', methods=['POST'])
def table():
    res = handle_file(request)
    # if res.get("filename") != None:
    #     predict_table(res.get("filename"))
    return res['msg']

@app.route('/pre_table')
def pre_table():
    predict_table("ta.jpg")
    return redirect("/live")

def handle_file(request, mode="ta"):
    if 'filename' not in request.files:
        return {"msg": 'no_file'}  # 傳回代表「沒有檔案」的訊息

    file = request.files['filename']  # 取得上傳檔

    if file.filename == '':
        return {"msg": 'empty'}       # 傳回代表「空白」的訊息

    if file:
        file_type = filetype.guess_extension(file)  # 判斷上傳檔的類型

        if file_type in ALLOWED_EXTENSIONS:
            file.stream.seek(0)
            filename = f"{mode}" + '.' + file_type

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # 傳回代表上傳成功的訊息以及檔名。
            return {"msg": 'ok', "filename": filename}
        else:
            return {"msg": 'type_error'}  # 傳回代表「檔案類型錯誤」的訊息


@app.route('/img/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=38999)
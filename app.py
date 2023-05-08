from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect
from arduino import *
from file_write import *
from parse_data import *
from read_file import *
import math
import time
import json
import random
import gpiozero
import pymysql;
import configparser as parser;

async_mode = None

app = Flask(__name__)

config = parser.ConfigParser()

config.read('config.cfg')
myhost = config.get('mysqlDB', 'host')
myuser = config.get('mysqlDB', 'user')
mypasswd = config.get('mysqlDB', 'passwd')
mydb = config.get('mysqlDB', 'db')


app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
db = pymysql.connect(host = myhost, user = myuser, passwd = mypasswd, db = mydb)
pointer = db.cursor()


def background_thread(args):
    temp_flag = False
    count = 0
    dataList = []
    btnV=""
    while True:
        data = get_data()
        print(data)
        if args:
          A = dict(args).get('A')
          if A == None:
              A = 1
          btnV = dict(args).get('btn_value')
        else:
          A = 1
        if btnV == "start":
            flag = 1
            temp_flag = False
        elif data[2] < 100:
            flag = 0
            temp_flag = True
        elif btnV == "stop":
            flag = 0
            temp_flag = False
        else:
            flag = 0
            temp_flag = False
        if flag == 1 or temp_flag:
            socketio.sleep(2)
            count += 1
            dataDict = {
                "id": count,
                "Humidity": data[0] * float(A),
                "Temperature": data[1] * float(A)}
            dataList.append(dataDict)
            socketio.emit('my_data',
                      {'humidity': data[0] * float(A), 'count': count, "temperature": data[1] * float(A)},
                      namespace='/test')
            write_to_file(data)
            data.clear()
        else:
            if len(dataList) > 0:
                data_str = str(dataList).replace("'", "\'")
                pointer.execute("INSERT INTO DATA (value) VALUES(%s)", (data_str))
                db.commit()
                dataList.clear()

@app.route('/')
def index():
    return render_template('index.html',async_mode=socketio.async_mode)

@app.route("/database")
def show_database():
    pointer.execute("SELECT * FROM DATA")
    data = pointer.fetchall()
    return str(data)

@app.route("/database/<string:num>", methods = ["GET"])
def show_data_by_id(num):
    pointer.execute("SELECT * FROM DATA WHERE id = %s", num)
    data = pointer.fetchall()
    return render_template('database_graph.html',async_mode=socketio.async_mode, Data = parse_data(data))

@app.route("/file", methods = ["GET"])
def show_data():
    data = read_file()
    return render_template('database_graph.html',async_mode=socketio.async_mode, Data = data)

@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    session['A'] = message['value']
    emit('my_response',
         {'data': "Amplitude is: " + session['A']})


@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!'})
    disconnect()

@socketio.on('initialize', namespace='/test')
def initialize():
    session['receive_count'] = session.get('receive_count', 0) + 1
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())
    emit('my_response', {'data': 'Initialized!', 'count': session['receive_count']})

@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my_response', {'data': 'Connected!', 'count': 0})

@socketio.on('click_event', namespace='/test')
def db_message(message):
    if message['value'] == "start":
        emit('my_response', {'data': 'Started!'})
    else:
        emit('my_response', {'data': 'Stopped!'})
    session['btn_value'] = message['value']
    

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80, debug=True)

from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect
import math
import time
import json
import random
import gpiozero

async_mode = None

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


def background_thread(args):
    count = 0
    dataList = []
    btnV=""
    while True:
        if args:
          A = dict(args).get('A')
          btnV = dict(args).get('btn_value')
        else:
          A = 1
        #print A
        if btnV == "start":
            flag = 1
        elif btnV == "stop":
            flag = 0
        else:
            flag = 0
        if flag == 1:
            print(args)
            socketio.sleep(2)
            count += 1
            prem = math.sin(time.time())
            dataDict = {
                "t": time.time(),
                "x": count,
                "y": float(A) * prem}
            dataList.append(dataDict)
            json_object = json.dumps(dataDict, indent=4)
            if len(dataList) > 0:
                # print(str(dataList))
                print(str(dataList).replace("'", "\""))
            socketio.emit('my_response',
                      {'data': float(A)*math.sin(time.time()), 'count': count},
                      namespace='/test')




@app.route('/')
def index():
    return render_template('index.html',async_mode=socketio.async_mode)

@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    session['A'] = message['value']
    emit('my_response',
         {'data': message['value'], 'count': session['receive_count']})


@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    if dict(session._get_current_object()).get('button_value') == "open":
        with thread_lock:
            if thread is None:
                thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())
        emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('click_event', namespace='/test')
def db_message(message):
    session['btn_value'] = message['value']

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80, debug=True)
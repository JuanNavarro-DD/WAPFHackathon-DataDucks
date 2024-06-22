from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

# from flask import Flask, render_template
# from flask_socketio import SocketIO, emit
# import time
# import threading

# app = Flask(__name__)
# socketio = SocketIO(app,cors_allowed_origins="*")

# def send_current_time():
#     while True:
#         current_time = time.strftime("%H:%M:%S", time.localtime())
#         socketio.emit('time_update', {'time': current_time})
#         print("sent time to client")
#         time.sleep(10)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @socketio.on('connect')
# def handle_connect():
#     print('Client connected')
#     send_current_time()



# if __name__ == '__main__':
#     # Start the background thread to send time updates
#     thread = threading.Thread(target=send_current_time)
#     thread.daemon = True
#     thread.start()
#     socketio.run(app)


# from flask import Flask,render_template,request
# from flask_socketio import SocketIO, emit
# import time
# import threading

# app = Flask(__name__)
# socketio = SocketIO(app,debug=True,cors_allowed_origins='*',async_mode='eventlet')


# @app.route('/')
# def index():
#     return render_template('index.html')

# @socketio.on("my_event")
# def send_current_time():
#     while True:
#         current_time = time.strftime("%H:%M:%S", time.localtime())
#         socketio.emit('time_update', {'time': current_time})
#         time.sleep(4)

# @socketio.on("my_event")
# def checkping():
#     for x in range(5):
#         cmd = 'ping -c 1 8.8.8.8|head -2|tail -1'
#         listing1 = subprocess.run(cmd,stdout=subprocess.PIPE,text=True,shell=True)
#         sid = request.sid
#         emit('server', {"data1":x, "data":listing1.stdout}, room=sid)
#         socketio.sleep(1)


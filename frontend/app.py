from flask import Flask, render_template
import requests, logging

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/keyword',methods=('GET','POST'))
def keyword():
    headers = {"content-type":"application/json","accept":"application/json" }
    r= requests.post('http://127.0.0.1:8000/extract',json={"transcript":"there's a fire in my house"},headers=headers)
    app.logger.info(r.text)
    return r.text


if __name__ == '__main__':
    app.run(debug=True)


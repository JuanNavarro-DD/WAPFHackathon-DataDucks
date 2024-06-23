from flask import Flask, render_template, request
import requests, logging
import json
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="wapolice",
    user="postgres",
    password="root!@3"
)

app = Flask(__name__)

@app.route('/')
def index():
    trans_txt = '{"questions":["Recommended questions"]}'
    trans_json = json.loads(trans_txt)
    trans = trans_json["questions"]
    etypes = "Summary of emergency"
    actions = 'Recommended action'
    botOutput = ""
    transc = ""
    return render_template('index.html',trans=trans, etypes=etypes, actions=actions, transc=transc, botOutput=botOutput)

@app.route('/keyword',methods=('GET','POST'))
def keyword():
    if request.method=='POST':
        transc = str(request.form.get("final_span"))
        emergency = str(request.form.get("emergency"))
        botOutput = str(request.form.get("botOutput"))
   
        headers = {"content-type":"application/json","accept":"application/json" }
        r= requests.post('http://127.0.0.1:8000/extract',json={"transcript":transc},headers=headers)
        
        json_object = json.loads(r.text)
        trans = json_object["questions"]
        etypes = json_object["Emergency Type"]
        actions = 'Please refer to '+json_object["Actions"]

        cur = conn.cursor()
        cur.execute(
        "INSERT INTO transcript (transcript, emergency_type, agent_comments, emergency_type_assist, actions) VALUES (%s, %s, %s, %s, %s)", 
        (transc, str(emergency), str(botOutput), str(etypes), str(actions)))
        conn.commit()

        return render_template("index.html", trans=trans, etypes=etypes, actions=actions, transc=transc, botOutput=botOutput)
    
if __name__ == '__main__':
    app.run(debug=True)


#Modified by smartbuilds.io
#Date: 27.09.20
#Desc: This web application serves a motion JPEG stream
# main.py
# import the necessary packages
from flask import Flask, render_template, Response, request, session, redirect
from camera import VideoCamera
import time
import threading
import os
import werkzeug
from werkzeug.utils import secure_filename
import cv2
import requests

pi_camera = VideoCamera(flip=False) # flip pi camera if upside down.

# App Globals (do not edit)
app = Flask(__name__)
app.config['SECRET_KEY'] = "15de2e5584da6716f650e3d50fa752cd"

@app.route('/')
def index():
    if "count" in session:
        session["count"]+=1
    else:
        session["count"] = 1
    return render_template('index.html') #you can customze index.html here

def gen(camera):
    #get camera frame
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
def capture(camera,project_id,count):
    frame = camera.set_frame()
    return cv2.imwrite(f"/home/pi/Desktop/pi-camera-stream-flask/{project_id}00{count}.jpg",frame)
@app.route('/video_feed')
def video_feed():
    return Response(gen(pi_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/captureimage')
def capture_image():
    try:
        check_flag = capture(pi_camera,session["session_id"]["pid"],session["count"])
        print (check_flag)
        if check_flag == True:
            post_image = requests.post("http://192.168.0.126:5000/upload", files={'file':open(f"{session['session_id']['pid']}00{session['count']}.jpg","rb")})
            if post_image.status_code == 202:
                print ("Success")
                return redirect("/")
            else:
                return ("Image gaya nhi")
            
        else:
            return ("Haga")
            
    except Exception as e:
        print (str(e))
        return (str(e))

@app.route("/setcred/<project_id>/<uid>")
def add_uid(project_id,uid):
    #session["uid"] = {"uid":str(uid),"pid":str(project_id)}
    session_file = open(f"{str(uid)}.txt","w")
    session_file.write(f"{project_id}")
    session_file.close()
    print (f"incoming parameters: {str(uid)}")
    return "Credentials Set", 200

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/verify", methods=["GET"])
def verify_login():
    try:
         
        session_file = open(f"{str(request.args.get('uid'))}.txt","r")
        proj = session_file.readline().replace("\n","")
        session_file.close()
        session["session_id"] = {"uid":str(request.args.get('uid')), "pid": str(proj) }
        session["count"] = 0
        return redirect("/")

    except Exception as e:
        print (str(e))
        return render_template("invalid.html")
    #return redirect("/login")

@app.route("/endsurvey")
def end_survey():
    try:
        send_data = requests.get(f"http://192.168.0.126:5000/makereport/{session['session_id']['uid']}/{session['session_id']['pid']}/{str(session['count'])}")
        os.system(f"rm {session['session_id']['uid']}.txt")
        session.pop('session_id',None)
        session.pop('count', None)
        
        
        return redirect ('/login')
        
    except Exception as e:
        print (str(e))
        return (str(e))
if __name__ == '__main__':

    app.run(host='0.0.0.0', debug=False)
    



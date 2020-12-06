from flask import Flask, render_template,request,flash,redirect,jsonify, session
from form import inputQuery
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail,Message
#from models import model
from geopy.geocoders import Nominatim
import webbrowser
import os
import cv2
import time
import PIL
from PIL import Image
import markdown
from weasyprint import HTML
from werkzeug.utils import secure_filename
# from helper.md import genReport
app = Flask(__name__)
app.config['SECRET_KEY'] = "15de2e5584da6716f650e3d50fa752cd"
app.config.from_object("config.Config")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://admin:admin@localhost/testdb_2"
app.config['SQLALCHEMY_ECHO']= True

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'jimbhadwachutiya69@gmail.com'
app.config['MAIL_PASSWORD'] = 'jaimaharashtra69'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

db= SQLAlchemy(app)     # Instance for database handling
mail = Mail(app)        # Instance for Email work
inp=[]

# Some global Variables
ml= str()
nm=str()
psswd=str()
log_ml=str()
log_psswd=str()
#define the table
class model(db.Model):
    __tablename__ = "userdetails"
    name = db.Column(db.String(15),nullable=False)
    emailid = db.Column(db.String(80),nullable=False,primary_key=True)
    password = db.Column(db.String(10), nullable=False)
    #data = db.Column(JSON)
    def serialize(self):
        return ({'name':self.name,'emailid':self.emailid,'password':self.password})

class ProjectModel(db.Model):
    __tablename__ = "projectdetails"
    username = db.Column(db.String(50), nullable=False)
    projectid = db.Column(db.Integer(), nullable=False,primary_key = True)
    projectname = db.Column(db.String(100), nullable=False)
    extent = db.Column(db.Numeric(), nullable= False)
    report = db.Column(db.Integer(), nullable= False)
    def serialize(self):
        return ({'username':self.username, 'projectid':self.projectid, 'projectname':self.projectname, 'extent':self.extent, 'report':self.report}) 

class ImagesModel(db.Model):
    __tablename__ = "imagesdetails"
    projectid = db.Column(db.Integer(), nullable=False)
    imagename = db.Column(db.String(20), nullable=False, primary_key = True)
    height = db.Column(db.Numeric(), nullable= False)
    
    def serialize(self):
        return ({'imagename':self.imagename, 'projectid':self.projectid, 'height':self.height})
@app.route('/')
def index():
    return render_template("login.html")


@app.route('/signup')
def sign():
    return render_template('signup.html')

@app.route('/mailer', methods=['GET'])
def mailer():
    ml = str(request.args.get("mail"))
    nm = str(request.args.get("nm"))
    psswd = str(request.args.get("psswd")) 
    session["ml"] = ml
    session["nm"] = nm
    session["psswd"] = psswd
    # code to send verification email
    try:
        msg = Message(subject="Email Verification",recipients=[ml],sender="jkhan266@gmail.com")
        msg.body="Greetings!Click on the http://127.0.0.1:5000/verif  to Proceed with verification."
        mail.send(msg)
        return render_template("register_mail.html")
    except Exception as e:
        return (str(e))
@app.route('/verif')
def verif():
    return render_template('verif.html')
@app.route('/inputTable', methods=['GET'])
def inpTab():
    # write the code to add values into the database
    try:
        print ("Values at insertion:")
        print (session["ml"])
        print (session["nm"])
        chk = model.query.filter_by(emailid=session["ml"]).count()
        print (chk)
        if chk !=0 :
            return render_template("<b>Sorry User with the Email already exists<b>. Go to the<a href='http://127.0.0.1:5000/'> Login page</a> and get going.</b>")
        else:
            mod = model(name=session["nm"],emailid=session["ml"],password=session["psswd"])
            db.session.add(mod)
            db.session.commit()
            return redirect('/')
    except Exception as e:
        return (str(e))

@app.route('/logCheck',methods=['GET'])
def lCheck():
    log_ml = str(request.args.get("mail"))
    log_psswd = str(request.args.get("psswd"))
    print (log_ml)
    # code to verify user exists
    try:
        chk = model.query.filter_by(emailid=log_ml).count()
        print (chk)
        if (chk == 0):
            return render_template("invalid_user.html")
        else:
            queryOut = model.query.filter_by(emailid=log_ml).first()
            #que= jsonify(queryOut.serialize())
            print (queryOut.password)
            if log_psswd == queryOut.password:
                session['emailid']=queryOut.emailid
                session['uname']=queryOut.name
                
                return redirect('/projects')
            else:
                return render_template("Sorry Password didn't Match. <a href='/'>Retry</a>")
    except Exception as e:
        return (str(e))

@app.route('/gen')
def frm():
    if ('emailid' and 'uname') in session:
        #form = inputQuery()
        data = session['uname']
        
       
        return render_template("form.html", data=data)
    else:
        return redirect('/')
@app.route('/exec', methods=['GET'])
def exec():
    inp=[]
    inp.append(str(request.args.get("loc")))
    inp.append(str(request.args.get("proj")))
    inp.append(float(request.args.get("ext")))
    session['project'] = inp[1]
    
    # inp.append(str(request.args.get("uname")))
    # inp.append(str(request.args.get("email")))
    commands = {"dir":["cd ~/Downloads","cd ~/.gazebo/models/"],"unzip":["unzip"],"move":["mv"],"list":["ls -a "]}
    dirs = ["~/Downloads/","~/.gazebo/","~/.gazebo/models/"]
    locate = Nominatim(user_agent="jkhan266@gmail.com")
    loc = inp[0]
    result =locate.geocode(loc)
    print (result)
    lat = [str(result.latitude), str(result.latitude+((0.170*(inp[2]))/18))]
    lon = [str(result.longitude), str(result.longitude+((0.170*(inp[2]))/18))]
    print(lat)
    print(lon)
    nm = inp[1]
    url = "http://terrain.party/api/export?name=" + nm + "&box="+ lon[0] + ","+ lat[0]+","+lon[1]+ ","+lat[1] 
    print (url)
    webbrowser.open(url)
    debug = webbrowser.open(url)
    if (debug):
        time.sleep(25)
        print ("success!!")
        command_01 = os.system("mkdir -p "+ dirs[2]+nm+"/materials/textures")
        if (command_01 == 0):
            time.sleep(5)
            print ("unzip "+dirs[0]+nm+"\ terrain.zip"+ " -d "+dirs[0]+nm+"\ terrain")
            command_02 = os.system("unzip "+dirs[0]+nm+"\ terrain.zip"+ " -d "+dirs[0]+nm+"\ terrain")
            if (command_02 == 0):
                print ("unzip successful")
                time.sleep(7)
                #img = cv2.imread(dirs[0]+nm+"\ terrain/"+nm+"\ Height"+ "\Map"+ "\(Merged).png")
                cmd = os.system("mv "+dirs[0]+nm+"\ terrain/"+nm+"\ Height\ Map\ \(Merged\).png" + " " + dirs[2]+nm+"/greyscale.png")
                cmd_01 = os.chdir("/home/jkhan01/.gazebo/models/"+nm+"/")
                img = Image.open("greyscale.png")
                img = img.resize((513,513),PIL.Image.ANTIALIAS)
                img_list = list(img.getdata())
                img_size =513      
                # Find minimum and maximum value pixels in the image
                img_max = max(img_list)
                img_min = min(img_list)

                # Determine factor to scale to a 8-bit image
                scale_factor = 255.0/(img_max - img_min)

                img_list_new = [0] * img_size * img_size

                # Rescale all pixels to the range 0 to 255 (in line with unit8 values)
                for i in range(0,img_size):
                    for j in range(0,img_size):
                        img_list_new[i*img_size + j] = int((img_list[i*img_size + j]-img_min)*scale_factor)
                        if (img_list_new[i*img_size + j] > 255) or (img_list_new[i*img_size + j] < 0) or (img_list_new[i*img_size + j]-int(img_list_new[i*img_size + j]) != 0):
                            print("img_list_new[%d][%d] = %r" % (i,j,img_list_new[i*img_size + j]))

                img.putdata(img_list_new)

                # Convert to uint8 greyscale image
                img = img.convert('L')

                # Save image
                img.save("greyscale.png")
                print ("Image at destination")
                pths = "/home/jkhan01/.gazebo/models/"+nm+"/model.sdf"
                pthc = "/home/jkhan01/.gazebo/models/"+nm+"/model.config"
                print (pths)
                sdf = open(pths,"a")
                st_sdf = ['<?xml version="1.0" ?>','<sdf version="1.5">','<model name="gazeboTerrain_01">',"<static>true</static>",
                            '<link name="link">','<collision name="collision">',"<geometry>",
                            "<heightmap>","<uri>model://"+nm+"/greyscale.png</uri>","<size>150 150 60</size>","<pos>0 0 0</pos>","</heightmap>","</geometry>","</collision>",
                            '<visual name="visual_abcedf">',
                            '<geometry>',
                                '<heightmap>',
                                '<use_terrain_paging>false</use_terrain_paging>',
                                '<texture>',
                                    '<diffuse>file://media/materials/textures/dirt_diffusespecular.png</diffuse>',
                                    '<normal>file://media/materials/textures/flat_normal.png</normal>',
                                    '<size>1</size>',
                                '</texture>',
                                '<texture>',
                                    '<diffuse>file://media/materials/textures/grass_diffusespecular.png</diffuse>',
                                    '<normal>file://media/materials/textures/flat_normal.png</normal>',
                                    '<size>1</size>',
                                '</texture>',
                                '<texture>',
                                    '<diffuse>file://media/materials/textures/fungus_diffusespecular.png</diffuse>',
                                    '<normal>file://media/materials/textures/flat_normal.png</normal>',
                                    '<size>1</size>',
                                    '</texture>',
                                    '<blend>',
                                        '<min_height>2</min_height>',
                                        '<fade_dist>5</fade_dist>',
                                    '</blend>',
                                    '<blend>',
                                        '<min_height>4</min_height>',
                                        '<fade_dist>5</fade_dist>',
                                    '</blend>',
                                    '<uri>model://'+nm+'/greyscale.png</uri>',
                                    '<size>150 150 60</size>',
                                    '<pos>0 0 0</pos>',
                                    "</heightmap>",
                                "</geometry>",
                                "</visual>",
                            "</link></model>  <!--/world-->",
                        "</sdf>"]
                print (st_sdf)
                for i in st_sdf:
                    sdf.write("\n"+i)
                sdf.close()
                std_config = ['<?xml version="1.0"?>','<model>','<name>',nm,'</name>','<version>1.0</version>',
                                '<sdf version="1.5">model.sdf</sdf>','<author>','<name>',session['uname'],'</name>','<email>',session['emailid'],'</email></author>',
                                '<description>A simple terrain generated for Basic Surveying.  </description></model>']
                config = open(pthc,"a")
                for j in std_config:
                    config.write("\n"+j)
                config.close()
    try:
        docMail = Message(subject="Output Files",recipients=[session['emailid']],sender="jkhan266@gmail.com",body="Kindly find the necessary files here!")
        with app.open_resource(pthc) as fread:
            docMail.attach("model.config","text/xml",fread.read())
        with app.open_resource(pths) as fread:
            docMail.attach("model.sdf","text/xml",fread.read())
        with app.open_resource("/home/jkhan01/.gazebo/models/"+nm+"/greyscale.png") as fread:
            docMail.attach("greyscale.png","image/png",fread.read())
        mail.send(docMail)
        proj = ProjectModel(username=session['uname'],projectname=session['project'],projectid=ProjectModel.query.count()+1,extent=inp[2],report = 0)
        db.session.add(proj)
        db.session.commit()
        return redirect ('/projects')
    except Exception as e:
        return (str(e))
    
@app.route('/projects')
def dashboard():
    if ('emailid' and 'uname') in session:
        data = [session['uname']]
        data.append(ProjectModel.query.filter_by(username=session['uname']).count())
        data.append(ProjectModel.query.filter_by(username=session['uname'],report=1).count())
        data.append(ProjectModel.query.filter_by(username=session['uname'],report=0).count())
        data.append(ProjectModel.query.filter_by(username=session['uname'], report=0))
        data.append(ProjectModel.query.filter_by(username=session['uname'], report=1))
        return render_template("dashboard.html", data= data)
    else:
        return redirect('/')

@app.route('/pending')
def listPending():
    if ('emailid' and 'uname') in session:
        data = [session['uname']]
        data.append(ProjectModel.query.filter_by(username=session['uname'],report=0).count())
        data.append(ProjectModel.query.filter_by(username=session['uname'],report=0))
        return render_template('listProjects.html',data=data)
    else:
        return('/')


@app.route('/reports')
def reports():
    if ('emailid' and 'uname') in session:
        data = [session['uname']]
        data.append(ProjectModel.query.filter_by(username=session['uname'],report=1).count())
        data.append(ProjectModel.query.filter_by(username=session['uname'],report=1))
        return render_template('reports.html',data=data)
    else:
        return redirect('/')

@app.route('/images/<projectid>')
def addImages(projectid):
    if ('emailid' and 'uname') in session:
        data = projectid 
        return render_template('imageForm.html',data=data)
    else:
        return ('/')

base_upload_path = '/static'
@app.route('/pushimages', methods=['POST'])
def pushImages():
    projectId = str(request.form['pid'])
    files = request.files.getlist('imgs')
    print (files)
    data = [projectId]
    data.append(len(files))
    os.system("mkdir /home/jkhan01/"+'Desktop/automatedSurveying/static/'+projectId+'/')
    os.system("mkdir /home/jkhan01/"+'Desktop/automatedSurveying/static/'+projectId+'/'+'images')
    for i in files:
        filename = secure_filename(i.filename)
        i.save(os.path.join('/home/jkhan01/Desktop/automatedSurveying/static/'+projectId+'/images/', filename))

    return render_template('heightData.html',data=data)

@app.route('/generatereport', methods=['GET'])
def heighData():
    try:
        projectId = str(request.args.get('pid'))
        pName = ProjectModel.query.filter_by(projectid=int(projectId)).first()
        heightDict = {}
        for j in range(1,int(request.args.get('length'))+1):
            heightDict[j] = str(request.args.get(str(j)))
        obj = genReport(heightDict,projectId,pName.projectname)
        mdScript = obj.generate_md()
        htmlScript = markdown.markdown(mdScript)
        pdfScript = HTML(string=htmlScript, base_url='/home/jkhan01/Desktop/automatedSurveying/static/'+projectId+'/')
        # with open(projectId+"report.pdf", "w"):
        pdfScript.write_pdf(projectId +"report.pdf")
        
        updateR = ProjectModel.query.filter_by(projectid= int(projectId)).first()
        updateR.report = 1
        db.session.commit()
        return redirect('/projects') 
    except Exception as e:
        return (str(e))


@app.route('/report/<pId>')
def report(pId):
    data = pId
    print (pId)
    return render_template('report_render.html', data=data)

@app.route('/logout')
def logOut():
    session.pop('emailid',None)
    session.pop('uname',None)
    session.pop('project', None)
    return redirect("/")
        

if __name__ == '__main__':
    app.run(debug=True)
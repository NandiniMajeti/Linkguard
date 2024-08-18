#importing required libraries

from flask import Flask, request, render_template,redirect
from pymongo import MongoClient
import numpy as np 
import warnings
import pickle
warnings.filterwarnings('ignore')
from feature import FeatureExtraction

file = open("pickle/model_phish.pkl","rb")
gbc = pickle.load(file)
file.close()

client = MongoClient('mongodb://127.0.0.1:27017')
db = client['users']
collection = db['user']
coll2 = db['links']

app = Flask(__name__)
@app.route('/',methods=["GET","POST"])
def home():
    title='Landing Page'
    return render_template('landingpage.html',title=title)

@app.route('/landing',methods=["GET","POST"])
def home1():
    title='Landing Page'
    return render_template('landingpage.html',title=title)

@app.route('/about',methods=["GET","POST"])
def about():
    title='About us'
    return render_template('about.html',title=title)

@app.route('/contact',methods=["GET","POST"])
def contact():
    title='contact Us'
    return render_template('contact.html',title=title)

@app.route("/features",methods=["GET","POST"])
def feature():
    title='Features'
    return render_template('features.html',title=title)

@app.route("/url-detection", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        obj = FeatureExtraction(url)
        x = np.array(obj.getFeaturesList()).reshape(1,30) 
        y_pred =gbc.predict(x)[0]
        print(y_pred)
        #1 is safe       
        #-1 is unsafe
        y_pro_phishing = gbc.predict_proba(x)[0,0]
        y_pro_non_phishing = gbc.predict_proba(x)[0,1]    
        if(y_pred==1):
            pred = "It is {0} % safe to go ".format(y_pro_phishing*100)
        else:
            pred = "It is {0:.2f} % unsafe to go ".format(y_pro_phishing*100)
        coll2.insert_one({"url":url,"responce":pred})
        data=coll2.find()       
        return render_template('index.html',xx =round(y_pro_non_phishing,2),url=url,data=data )
    data=coll2.find()    
    return render_template("index.html", xx =-1,data=data)

@app.route('/login',methods=['POST'])
def login():
    email = request.form['uname']
    password = request.form['pass']
    user =collection.find_one({"email":email})
    if user and user['password'] == password:
        return redirect('/url-detection')
    else:
        return render_template('landingpage.html')
    
@app.route("/register",methods=['post'])
def regis():
    name=request.form['name']
    email = request.form['email']
    passs= request.form['password']
    con_pass= request.form['confirm-password']    
    if (passs==con_pass):
        collection.insert_one({"name":name,"email":email,"password":passs})
        return  render_template('landingpage.html')
    else:
        return render_template("signup.html",res="Registration unsuccesful")
    
    
@app.route("/regis")
def regispage():
    return render_template("signup.html")


if __name__ == "__main__":
    app.run()
from flask import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import pymysql
from models import app,User,City,db
from flask_login import LoginManager,login_user
from form import LoginForm
import requests

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route("/",methods=["GET","POST"])
def login():

    if request.method=="POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            return redirect(url_for('login'))

        return redirect(url_for('index',id=user.id))

    return render_template('login.html')

@app.route('/signup',methods=["GET","POST"])
def signup():
    if request.method=="POST":
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists')
            return redirect(url_for('signup'))
        
        new_user = User(email=email, username=username, password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    return redirect(url_for('login'))

@app.route('/index/<string:id>',methods=["GET","POST"])
def index(id):
    if request.method=="POST":
        city=request.form.get("city")

        duplicate= City.query.filter_by(name=city,user_id=id).first()
        if city and (duplicate is None):
            new_city = City(name=city,user_id=id)
            db.session.add(new_city)
            db.session.commit()


    cities = City.query.filter_by(user_id=id)

    url="https://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=fbe2be5555d75f3901e721cc5605867d"
    
    cities_list=[]
    for citydb in cities:
        r=requests.get(url.format(citydb.name)).json()
        weather={
        "user_id":citydb.user_id,
        "id":citydb.id,
        "city":citydb.name,
        "temperature":r["main"]["temp"],
        "description":r["weather"][0]["description"],
        "icon":r["weather"][0]["icon"],
        }
        cities_list.append(weather)

    
    return render_template("index.html",id=id,cities_list=cities_list)


@app.route('/deleteCity/<string:userId>/<string:cityID>')
def deleteCity(userId,cityID):

    City.query.filter_by(id=cityID).delete()
    db.session.commit()
    return redirect(url_for('index',id=userId))

@app.route('/update/<string:userId>',methods=["POST","GET"])
def updateUser(userId):
    update_user= User.query.get(userId)
    if request.method=="POST":
        update_user.email = request.form.get('email')
        update_user.username =request.form.get('username')
        update_user.password =request.form.get('password')
        db.session.commit()    
        return redirect(url_for("login"))
    return render_template("profil.html",obje=update_user)

@app.route('/delete/<string:userId>')
def deleteUser(userId):

    City.query.filter_by(user_id=userId).delete()
    User.query.filter_by(id=userId).delete()
    db.session.commit()

    return redirect(url_for('login'))


if __name__=='__main__':
    app.run(debug=True)


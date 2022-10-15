import base64
import os
from datetime import timedelta
from functools import wraps
from random import randint, choice
import pymongo as pymongo

from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_bootstrap import Bootstrap
from werkzeug.urls import url_encode

from utils import databaseUtils, gameUtils


UPLOAD_FOLDER = "static/"
rooms = dict()


def require_login(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if 'user' not in session:
            flash("Please log in to create posts")
            return redirect(url_for("login"))
        else:
            return f(*args, **kwargs)

    return inner


app = Flask(__name__)
app.secret_key = os.urandom(16)
Bootstrap(app)

client = pymongo.MongoClient("mongodb+srv://admin:pass@cluster0.idxdfmn.mongodb.net/?retryWrites=true&w=majority")

@app.template_global()
def modify_query(origin, **new_values):
    args = request.args.copy()

    for key, value in new_values.items():
        args[key] = value

    return '{}?{}'.format(origin, url_encode(args))


@app.route('/')
def root():
    return render_template("home.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect(url_for('login'))


@app.route("/join")
def join():
    return render_template("joinRoom.html")


@app.route("/room/<key>")
def room(key):
    if key in rooms:
        rooms[key]['players'].add(session['user'])
        return render_template("room.html", room_data=rooms[key])
    flash("Room does not exist!")


@app.route("/createRoom")
def createRoom():
    return render_template("createRoom.html")


# Utility Routes, you do not stay on these pages
@app.route("/addRoom", methods=["POST"])
def addRoom():
    key = []
    game = None
    while True:
        for i in range(4):
            key.append(choice(gameUtils.alphanumeric))
        key = ''.join(key)
        if key not in rooms:
            break

    rooms[key] = dict()
    rooms[key]['game'] = game
    rooms[key]['players'] = session['user']
    return redirect(url_for("room", key=key))


# If Uploading Images Is Required
@app.route("/imgUP", methods=["POST"])
def imgUP():
    print("Uploading")
    data = request.form["url"]
    encoded_data = data.split(',')[1]
    decoded_data = base64.b64decode(encoded_data)
    filename = "img/" + str(randint(0, 999999999999)) + ".png"
    print(filename)
    filepath = UPLOAD_FOLDER + filename
    f = open(filepath, "wb")
    f.write(decoded_data)
    f.close()
    url = databaseUtils.upload_blob("pandora-engine-bucket", filepath, str(randint(0, 999999999999)))
    session['img_url'] = url
    return redirect(url_for("", img_url=url))


@app.route("/auth", methods=["POST", "GET"])
def auth():
    if "submit" not in request.form or "user" not in request.form or "pwd" not in request.form:
        flash("At least one form input was incorrect")
        return redirect(url_for('login'))

    if request.form['submit'] == 'Login':
        user = databaseUtils.authenticate(client, request.form['user'], request.form['pwd'])
        if user:
            session['user'] = str(user)
            session['username'] = databaseUtils.get_user_by_id(client, user)['username']
            session.permanent = True
            app.permanent_session_lifetime = timedelta(minutes=30)
            return redirect(url_for('root'))
        else:
            flash('Incorrect username or password')
            return redirect(url_for('login'))
    else:
        success = databaseUtils.create_user(client, request.form['user'], request.form['pwd'])
        if success:
            session['user'] = str(success)
            session['username'] = databaseUtils.get_user_by_id(client, success)['username']
            session.permanent = True
            app.permanent_session_lifetime = timedelta(minutes=30)
            return redirect(url_for('root'))
        else:
            flash('This username already exists!')
            return redirect(url_for('login'))


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')

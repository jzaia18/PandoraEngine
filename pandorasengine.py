import base64
import json
import os
from datetime import timedelta
from functools import wraps
from random import randint, choice
import pymongo as pymongo

from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_bootstrap import Bootstrap
from werkzeug.urls import url_encode

from utils import databaseUtils, gameUtils, widgets

UPLOAD_FOLDER = "static/"


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
        room = databaseUtils.get_user_by_id(app.client, session['user'])['room']
        databaseUtils.delete_room(app.client, room)
        databaseUtils.clear_user_room(app.client, session['username'])
        session.pop('user')
    return redirect(url_for('login'))


@app.route("/join")
def join():
    return render_template("joinRoom.html")


@app.route("/room/<key>")
def room(key):
    room_data = databaseUtils.get_room_by_key(app.client, key)
    if room_data:
        databaseUtils.add_user_to_room(app.client, key, databaseUtils.get_user_by_id(app.client, session['user']))
        return render_template("room.html", room_data=room_data)
    flash("Room does not exist!")
    return redirect(url_for('join'))


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
        if not databaseUtils.get_room_by_key(app.client, key):
            break

    databaseUtils.clear_user_room(app.client, session['user'])
    databaseUtils.create_room(app.client, key, session['user'], [], game)
    databaseUtils.add_room_to_user(app.client, session['username'], key)
    return redirect(url_for("room", key=key))


@app.route("/editor")
def editor():
    return render_template("editor.html")


@app.route("/widget/new/text", methods=['POST'])
def widget_new_text():
    if 'text' not in request.form:
        return None  # Error

    return str(widgets.create_text_widget(app.client, request.form['text']))


@app.route("/widget")
def widget():
    if 'widget_id' not in request.args:
        return None  # Error

    return widgets.get_widget(app.client, request.args['widget_id'])


@app.route("/joinRoom", methods=["POST"])
def joinRoom():
    return redirect(url_for("room", key=request.form['key']))


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


@app.route("/test")
def test():
    return render_template("game.html")


@app.route("/game")
def game():
    # TODO: send initial widget

    # TEST CODE (and pass `widget=widget` to `render_template`):
    # widget = widgets.get_widget(app.client, "634adeb7b0f28a5d9c7dd5c3")
    # widget['_id'] = str(widget['_id'])
    return render_template("game.html")


@app.route("/validateWidget", methods=["GET", "POST"])
def validateWidget():
    verity = True
    if request.form['widget_type'] == 'text':
        if not request.form['contents']:
            verity = False

    elif request.form['widget_type'] == 'image':
        if not request.form['contents']:
            verity = False

    elif request.form['widget_type'] == 'text_input':
        if not request.form['contents']:
            verity = False

    elif request.form['widget_type'] == 'choice':
        if not request.form['contents']:
            verity = False

    elif request.form['widget_type'] == 'timer':
        if not request.form['value'] or not isinstance(request.form['value'], int):
            verity = False
    else:
        flash("Invalid Widget Type**DEBUG ERROR")

    return { 'verity': verity }


@app.route("/generateWidgets", methods=["GET", "POST"])
def generateWidgets():
    response = dict()
    for field in request.form:
        if field['widget_type'] == 'text':
            widget_id = widgets.create_text_widget(app.client, field['contents'])
            response[widget_id] = widgets.get_widget(app.client, widget_id)

        elif field['widget_type'] == 'image':
            widget_id = widgets.create_image_widget(app.client, field['contents'])
            response[widget_id] = widgets.get_widget(app.client, widget_id)

        elif field['widget_type'] == 'text_input':
            widget_id = widgets.create_text_input_widget(app.client, field['contents'])
            response[widget_id] = widgets.get_widget(app.client, widget_id)

        elif field['widget_type'] == 'choice':
            widget_id = widgets.create_choice_widget(app.client, field['contents'])
            response[widget_id] = widgets.get_widget(app.client, widget_id)

        elif field['widget_type'] == 'timer':
            flash("Implement this my boi")

        else:
            flash("Invalid Widget Type**DEBUG ERROR")

    return response

@app.route("/auth", methods=["POST", "GET"])
def auth():
    if "submit" not in request.form or "user" not in request.form or "pwd" not in request.form:
        flash("At least one form input was incorrect")
        return redirect(url_for('login'))

    if request.form['submit'] == 'Login':
        user = databaseUtils.authenticate(app.client, request.form['user'], request.form['pwd'])
        if user:
            session['user'] = str(user)
            session['username'] = databaseUtils.get_user_by_id(app.client, user)['username']
            session.permanent = True
            app.permanent_session_lifetime = timedelta(minutes=30)
            return redirect(url_for('root'))
        else:
            flash('Incorrect username or password')
            return redirect(url_for('login'))
    else:
        success = databaseUtils.create_user(app.client, request.form['user'], request.form['pwd'])
        if success:
            session['user'] = str(success)
            session['username'] = databaseUtils.get_user_by_id(app.client, success)['username']
            session.permanent = True
            app.permanent_session_lifetime = timedelta(minutes=30)
            return redirect(url_for('root'))
        else:
            flash('This username already exists!')
            return redirect(url_for('login'))


if __name__ == '__main__':
    app.client = pymongo.MongoClient(
        "mongodb+srv://admin:pass@cluster0.idxdfmn.mongodb.net/?retryWrites=true&w=majority")
    app.debug = True
    app.run(host='0.0.0.0')

import base64
import json
import os
from datetime import timedelta
from functools import wraps
from random import randint, choices, shuffle
import pymongo as pymongo
from bson import ObjectId

from flask import Flask, jsonify, render_template, request, redirect, flash, url_for, session, abort
from flask_bootstrap import Bootstrap
from werkzeug.urls import url_encode

from utils import databaseUtils, gameUtils, widgets

UPLOAD_FOLDER = "static/"


def require_login(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if 'user' not in session:
            flash("Please log in")
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
@require_login
def join():
    return render_template("joinRoom.html")


@app.route("/room/<key>/players")
@require_login
def get_room_players(key):
    room_data = databaseUtils.get_room_by_key(app.client, key)
    if not room_data:
        return '', 400
    if not databaseUtils.user_in_room(app.client, room_data, session['user']):
        return '', 403
    return jsonify([player['username'] for player in room_data['players']])


@app.route("/room/<key>/state")
@require_login
def get_room_state(key):
    room_data = databaseUtils.get_room_by_key(app.client, key)
    if not room_data:
        return '', 400
    if not databaseUtils.user_in_room(app.client, room_data, session['user']):
        return '', 403

    if room_data['current_widget'] == -1:
        return {
            'widget_index': -1,
            'players': [player['username'] for player in room_data['players']],
        }
    # print(room_data)
    game = databaseUtils.get_game_by_id(app.client, room_data['game'])
    # print(game)
    widget = widgets.get_widget(app.client, game['widgets'][room_data['current_widget']])
    widget['_id'] = str(widget['_id'])
    # SCUFFED BUT NO TIME:
    if widget['widget_type'] == 'choice' and type(widget['choices']) == list:
        shuffle(widget['choices'])
    return {
        'widget_index': room_data['current_widget'],
        'widget': widget,
    }


@app.route("/room/<key>")
@require_login
def room(key):
    room_data = databaseUtils.get_room_by_key(app.client, key)
    if room_data:
        is_host = session['user'] == room_data['host']
        if not is_host:
            databaseUtils.add_user_to_room(app.client, key, databaseUtils.get_user_by_id(app.client, session['user']))
        return render_template("room.html", room_data=room_data, is_host=is_host)
    flash("Room does not exist!")
    return redirect(url_for('join'))


@app.route("/room/<key>/begin")
@require_login
def startRoom(key):
    room_data = databaseUtils.get_room_by_key(app.client, key)
    if not room_data:
        return '', 400
    if room_data['host'] != session['user'] or room_data['current_widget'] != -1:
        return '', 403
    databaseUtils.inc_room_widget(app.client, key)
    response = redirect(url_for("get_room_state", key=key))
    response.mimetype = "application/json"
    return response


@app.route("/createRoom")
def createRoom():
    return render_template("createRoom.html", games=databaseUtils.get_games(app.client))


# Utility Routes, you do not stay on these pages
@app.route("/addRoom", methods=["GET", "POST"])
@require_login
def addRoom():
    key = []
    # game = databaseUtils.get_game_by_id(app.client, request.form['gameID'])
    gameID = ObjectId(request.form['gameID'])
    key = ''.join(choices(gameUtils.alphanumeric, k=4))

    databaseUtils.clear_user_room(app.client, session['user'])
    databaseUtils.create_room(app.client, key, session['user'], [], gameID)
    databaseUtils.add_room_to_user(app.client, session['username'], key)
    return redirect(url_for("room", key=key))


@app.route("/editor")
@require_login
def editor():
    return render_template("editor.html")


@app.route("/widget/new/text", methods=['POST'])
def widget_new_text():
    if 'text' not in request.form:
        return None  # Error

    return str(widgets.create_text_widget(app.client, request.form['text']))


@app.route("/widget/new/text_input", methods=['POST'])
def widget_new_text_input():
    if 'prompt' not in request.form:
        return None  # Error

    return str(widgets.create_text_input_widget(app.client, request.form['prompt']))


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
    return render_template("test.html")


@app.route("/game")
def game():
    # TODO: send initial widget

    # TEST CODE (and pass `widget=widget` to `render_template`):
    widget = widgets.get_widget(app.client, "634adeb7b0f28a5d9c7dd5c3")
    widget['_id'] = str(widget['_id'])
    return render_template("game.html", widget=widget)


@app.route("/validateWidget", methods=["POST"])
def validateWidget():
    if request.form['widget_type'] == 'text':
        if not request.form['contents']:
            abort(400)

    elif request.form['widget_type'] == 'image':
        if not request.form['contents']:
            abort(400)

    elif request.form['widget_type'] == 'text_input':
        if not request.form['contents']:
            abort(400)

    elif request.form['widget_type'] == 'choice':
        if not request.form['contents'] or not request.form['random'] or \
                (not request.form['choices'] and not request.form['random']) or not request.form['opinion']:
            abort(400)

    else:
        flash("Invalid Widget Type**DEBUG ERROR")

    return {}


@app.route("/generateWidgets", methods=["POST"])
def generateWidgets():
    response = list()
    for field in request.form:
        widget = json.loads(request.form[field])

        if widget['widget_type'] == 'text':
            widget_id = widgets.create_text_widget(app.client, widget['contents'], widget['timer'])
            response.append(str(widget_id))

        elif widget['widget_type'] == 'image':
            widget_id = widgets.create_image_widget(app.client, widget['contents'], widget['timer'])
            response.append(str(widget_id))

        elif widget['widget_type'] == 'text_input':
            widget_id = widgets.create_text_input_widget(app.client, widget['contents'], widget['timer'])
            response.append(str(widget_id))

        elif widget['widget_type'] == 'choice':
            widget_id = widgets.create_choice_widget(app.client, widget['contents'],
                                                     widget['choices'] and json.loads(widget['choices']),
                                                     widget['random'], widget['opinion'], widget['timer'])
            response.append(str(widget_id))

        else:
            print(field)
            flash("Invalid Widget Type**DEBUG ERROR")

    return {'widgets': response}


@app.route("/addGame", methods=["POST"])
def addGame():
    name = request.form['name']
    max_players = request.form['max_players']
    widgets = json.loads(request.form['widgets'])
    widgets = [ObjectId(x) for x in widgets]

    if name and max_players and widgets:
        databaseUtils.create_game(app.client, name, max_players, widgets)
        flash("Game Created Successfully!")
        return {}

    abort(400)


@app.route("/questionSubmission")
def questionSubmission():
    return render_template("questionSubmission.html")


@app.route("/submitQuestion", methods=["POST"])
def submitQuestion():
    question = request.form['question']
    answers = []
    for key in request.form:
        if 'McA' in key:
            answers.append(request.form[key])
    correct = request.form['correct']
    tags = request.form['tags'].split(",")
    databaseUtils.create_fact_multiple_choice(app.client, question, correct, answers, tags)
    flash("Question Submitted!")
    return redirect(url_for("questionSubmission"))


@app.route("/room/<key>/submit/<index>", methods=["POST"])
def answer(key, index):
    room = databaseUtils.get_room_by_key(app.client, key)
    question = room['game']['widgets'][int(index)]

    if request.form['answer'] == question['correct_answer']:
        flash("Correct Answer")
        data = {"verity": True}
        response = app.response_class(response=data, status=200, mimetype='application/json')
        return response

    data = {"verity": False}
    response = app.response_class(response=data, status=400, mimetype='application/json')
    return response

@app.route("/room/<key>/next")
def move_to_next_widget(key):
    databaseUtils.inc_room_widget(app.client, key)
    return {}



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

from _sha256 import sha256
from bson import ObjectId
from google.cloud import storage
import pymongo as pymongo
import base64
import gridfs


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )

    return "https://storage.cloud.google.com/pandora-engine-bucket/" + destination_blob_name


def create_game(client, name, max_players, widgets):
    db = client.Games
    games = db.games

    game = games.insert_one({
        "name": name,
        "num_players": 0,
        "max_players": max_players,
        "widgets": widgets
    })

    return game


def create_room(client, key, host, players, game):
    db = client.Rooms
    rooms = db.rooms

    room = rooms.insert_one({
        "key": key,
        "host": host,
        "players": players,
        "game": game})

    return room.inserted_id

# `fact` => one correct answer
# `opinion` => no correct answer

def create_fact_multiple_choice(client, prompt, correct_answer, fake_answers, tags):
    db = client.Questions
    qs = db.fact_mc
    
    question = qs.insert_one({
        "prompt": prompt,
        "correct_answer": correct_answer,
        "fake_answers": fake_answers,
        "tags": tags,
    })
    
    return question.inserted_id

def create_opinion_multiple_choice(client, prompt, choices, tags):
    db = client.Questions
    qs = db.opinion_mc
    
    question = qs.insert_one({
        "prompt": prompt,
        "choices": choices,
        "tags": tags,
    })
    
    return question.inserted_id


def create_fact_free_response(client, prompt, correct_answer, tags):
    db = client.Questions
    qs = db.fact_fr
    
    question = qs.insert_one({
        "prompt": prompt,
        "correct_answer": correct_answer,
        "tags": tags,
    })
    
    return question.inserted_id


def get_fact_multiple_choices_by_tag(client, tag):
    db = client.Questions
    qs = db.fact_mc
    
    return qs.find({"tags": tag})


def get_opinion_multiple_choices_by_tag(client, tag):
    db = client.Questions
    qs = db.opinion_mc
    
    return qs.find({"tags": tag})


def get_room_by_key(client, key):
    db = client.Rooms
    rooms = db.rooms

    return rooms.find_one({"key": key})


def add_user_to_room(client, key, user):
    db = client.Rooms
    rooms = db.rooms

    return rooms.update_one({"key": key}, {"$addToSet": {"players": user}})


def delete_room(client, key):
    db = client.Rooms
    rooms = db.rooms

    return rooms.delete_one({"key": key})


# creates a user in the database with a username, password, and post id
def create_user(client, username, password):
    db = client.Users
    users = db.users

    if get_user_by_name(client, username) is None:
        user = users.insert_one({
            "username": username,
            "password": hash_password(username, password),
            "room": None})
        return user.inserted_id
    return None


# gets the username of a user
def get_user_by_name(client, username):
    db = client.Users
    users = db.users

    return users.find_one({"username": username})


# gets the id of a user
def get_user_by_id(client, userid):
    db = client.Users
    users = db.users

    return users.find_one({"_id": ObjectId(userid)})


def add_room_to_user(client, username, key):
    db = client.Users
    users = db.users
    print("ADD ROOM " + key + " TO USER " + username)

    return users.update_one({"username": username}, {"$set": {"room": key}})


def clear_user_room(client, username):
    db = client.Users
    users = db.users

    return users.update_one({"username": username}, {"$set": {"room": None}})


# constructs the value for a password key
def hash_password(username, password):
    return sha256(str(username+password).encode('utf-8')).hexdigest()


# provides the information needed for a user to sign in
def authenticate(client, username, password):
    user = get_user_by_name(client, username)
    if user is None:
        return
    if hash_password(username, password) != user["password"]:
        return
    return user["_id"]


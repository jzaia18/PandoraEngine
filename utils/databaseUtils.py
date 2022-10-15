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


# creates a user in the database with a username, password, and post id
def create_user(client, username, password):
    db = client.Users
    users = db.users

    if get_user_by_name(client, username) is None:
        user = users.insert_one({
            "username": username,
            "password": hash_password(username, password),
            "postId": []})
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


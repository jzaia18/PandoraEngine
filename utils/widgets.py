from bson import ObjectId
from bson.json_util import dumps
import pymongo as pymongo

def create_text_widget(client, text):
    db = client.Games
    widgets = db.widgets
    
    new_widget = widgets.insert_one({
        'widget_type': 'text',
        'contents': text
    })

    return new_widget.inserted_id

def get_widget(client, widget_id):
    db = client.Games
    widgets = db.widgets

    return dumps(widgets.find_one({
        '_id': ObjectId(widget_id)
    }))

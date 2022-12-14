from bson import ObjectId
from bson.json_util import dumps
import pymongo as pymongo
from functools import wraps


def widget_creator(f): 
    @wraps(f)
    def wrapper(client, *args, **kwargs):
        db = client.Games
        widgets = db.widgets
        
        new_widget = widgets.insert_one(f(*args, **kwargs))
        return new_widget.inserted_id
    
    return wrapper


@widget_creator
def create_text_widget(text, timer):
    return {
        'widget_type': 'text',
        'contents': text,
        'timer': timer
    }


@widget_creator
def create_image_widget(href, timer):
    return {
        'widget_type': 'image',
        'contents': href,
        'timer': timer
    }


@widget_creator
def create_text_input_widget(prompt, timer):
    return {
        'widget_type': 'text_input',
        'contents': prompt,
        'timer': timer
    }


@widget_creator
def create_choice_widget(contents, choices, random, opinion, timer):
    return {
        'widget_type': 'choice',
        'contents': contents, # Will be either tags or the question itself
        'random': random,
        'choices': choices, # Null for randomized questions
        'opinion': opinion,
        'timer': timer
    }


def get_widget(client, widget_id):
    db = client.Games
    widgets = db.widgets

    return widgets.find_one({
        '_id': ObjectId(widget_id)
    })

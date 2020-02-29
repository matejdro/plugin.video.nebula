import storage
import requests
import xbmc
import re
import json

class InvalidCredentials(Exception):
    pass

def login():
    body = {
        "email": storage.get_saved_username(),
        "password": storage.get_saved_password()
    }

    user_data = requests.post("https://api.watchnebula.com/api/v1/auth/login/", json=body)
    if user_data.status_code != 200:
        raise InvalidCredentials()

    result_json = user_data.json()

    storage.set_nebula_token(result_json["key"])

def fetch_channel_list():
    html_result = requests.get("https://watchnebula.com").text

    initial_state = re.search('<script id="initial-app-state" type="application/json">((.|\n)*?)</script>', html_result).group(1)
    return json.loads(initial_state)

def get_channel_list():
    return fetch_channel_list()

def get_categories():
    categories = [(k,v) for k,v in get_channel_list()["categories"]["byTitle"].items() if k[0] != "_"]
    categories.sort(key=lambda a: a[0])

    return categories
    
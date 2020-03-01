import storage
import requests
import xbmc
import re
import json
import datetime
import time

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

def _refresh_channel_list():
    html_result = requests.get("https://watchnebula.com").text

    initial_state = re.search('<script id="initial-app-state" type="application/json">((.|\n)*?)</script>', html_result).group(1)
    storage.save_cached_channels(json.loads(initial_state))

def _get_channel_list():
    # Channel list rarely changes
    # To speed up user's experience, cache channel list
    # for 12 hours

    last_cache_time = storage.get_last_cache_date()
    now = int(time.mktime(datetime.datetime.now().timetuple()))

    if now - last_cache_time > 3600 * 12:
        _refresh_channel_list()

    return storage.get_cached_channels()

def get_categories():
    categories = [(k,v) for k,v in _get_channel_list()["categories"]["byTitle"].items() if (k[0] != "_" and k != "YouTube Channel")]
    categories.sort(key=lambda a: a[0])

    return categories

def get_channels_in_category(category_title):
    channels = [v for k,v in _get_channel_list()["channels"]["byID"].items() if v["genre"] == category_title]
    channels.sort(key=lambda a: a["title"])

    return channels

def get_all_channels():
    channels = [v for k,v in _get_channel_list()["channels"]["byID"].items()]
    channels.sort(key=lambda a: a["title"])

    return channels


from . import storage
import requests
import xbmc
import re
import json
import datetime
import time

USER_AGENT = "Unofficial Kodi extension for Nebula - https://github.com/matejdro/plugin.video.nebula"
HEADERS_WITH_ONLY_USER_AGENT = {
    "User-Agent": USER_AGENT
}


class InvalidCredentials(Exception):
    pass


def login():
    body = {
        "email": storage.get_saved_username(),
        "password": storage.get_saved_password()
    }

    user_token_body = requests.post(
        "https://api.watchnebula.com/api/v1/auth/login/",
        json=body,
        headers=HEADERS_WITH_ONLY_USER_AGENT
    )

    if user_token_body.status_code != 200:
        raise InvalidCredentials()

    result_json = user_token_body.json()

    storage.set_nebula_token(result_json["key"])

    user_data_headers = {
        "User-Agent": USER_AGENT,
        "Authorization": "Token " + storage.get_nebula_token()
    }

    requests.post(
        "https://api.watchnebula.com/api/v1/zype/auth-info/new/",
        headers=user_data_headers,
        json={}
    ).raise_for_status()

    user_data_body = requests.get(
        "https://api.watchnebula.com/api/v1/zype/auth-info/",
        headers=user_data_headers
    )
    user_data_body.raise_for_status()

    xbmc.log("ABCD", xbmc.LOGERROR)
    xbmc.log("Text: " + user_data_body.text, xbmc.LOGERROR)

    storage.set_zype_token(
        user_data_body.json()["access_token"]
    )

def _refresh_channel_list():
    json_result = requests.get("https://api.zype.com/zobjects",
                    headers=HEADERS_WITH_ONLY_USER_AGENT,
                    params={
                        "zobject_type": "channel",
                        "per_page": 500,
                        "api_key": "JlSv9XTImxelHi-eAHUVDy_NUM3uAtEogEpEdFoWHEOl9SKf5gl9pCHB1AYbY3QF"
                    }
                    ).json()["response"]

    storage.save_cached_channels(json_result)


def _get_channel_list():
    # Channel list rarely changes
    # To speed up user's experience, cache channel list
    # for 12 hours

    last_cache_time = storage.get_last_cache_date()
    now = int(time.mktime(datetime.datetime.now().timetuple()))

    if now - last_cache_time > 3600 * 12:
        _refresh_channel_list()

    return storage.get_cached_channels()


def get_video_manifest(video_id, relogin_on_fail=True):
    response = requests.get("https://player.zype.com/manifest/" + video_id + ".m3u8",
                            headers=HEADERS_WITH_ONLY_USER_AGENT,
                            params={
                                "access_token": storage.get_zype_token(),
                                "ad_enabled": "false",
                                "https": "true",
                                "preview": "false"
                            })

    # API sometimes returns 404 if user is not logged in...
    if response.status_code == 401 or response.status_code == 404:
        login()
        return get_video_manifest(video_id, relogin_on_fail=False)

    response.raise_for_status()

    lines = response.text.splitlines()
    playlist_entries = []
    for i in range(1, len(lines) - 1):
        playlist_entries.append((lines[i], lines[i + 1]))

    return playlist_entries


def get_categories():
    categories = list(set([channel["genre"] for channel in _get_channel_list() if channel["genre"] is not None]))
    categories.sort()


    return categories


def get_channels_in_category(category_title):
    channels = [channel for channel in _get_channel_list() if channel["genre"] == category_title]
    channels.sort(key=lambda a: a["title"])

    return channels


def get_channel_by_id(id):
    return next(iter([channel for channel in _get_channel_list() if channel["_id"] == id]))


def get_all_channels():
    channels = _get_channel_list()
    channels.sort(key=lambda a: a["title"])

    return channels


def get_all_videos(page):
    return requests.get("https://api.zype.com/videos",
                        headers=HEADERS_WITH_ONLY_USER_AGENT,
                        params={
                            "order": "desc",
                            "page": page,
                            "per_page": 20,
                            "sort": "published_at",
                            "api_key": "JlSv9XTImxelHi-eAHUVDy_NUM3uAtEogEpEdFoWHEOl9SKf5gl9pCHB1AYbY3QF"
                        }
                        ).json()["response"]

def get_channel_videos(channel, page):
    return requests.get("https://api.zype.com/videos",
                        headers=HEADERS_WITH_ONLY_USER_AGENT,
                        params={
                            "order": "desc",
                            "page": page,
                            "per_page": 20,
                            "sort": "published_at",
                            "playlist_id.inclusive": channel["playlist_id"],
                            "api_key": "JlSv9XTImxelHi-eAHUVDy_NUM3uAtEogEpEdFoWHEOl9SKf5gl9pCHB1AYbY3QF"
                        }
                        ).json()["response"]

def search(query):
    return requests.get("https://api.zype.com/videos",
                        headers=HEADERS_WITH_ONLY_USER_AGENT,
                        params={
                            "q": query,
                            "api_key": "JlSv9XTImxelHi-eAHUVDy_NUM3uAtEogEpEdFoWHEOl9SKf5gl9pCHB1AYbY3QF"
                        }
                        ).json()["response"]

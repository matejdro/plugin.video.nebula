import storage
import requests
import xbmc
import re
import json
import datetime
import time

USER_AGENT = "Unofficial Kodi extension for Nebula - https://github.com/matejdro/kodi-nebula"
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

    user_data_body = requests.get(
        "https://api.watchnebula.com/api/v1/auth/user/",
        headers=user_data_headers
    )
    user_data_body.raise_for_status()

    storage.set_zype_token(user_data_body.json()[
                           "zype_auth_info"]["access_token"])


def _refresh_channel_list():
    html_result = requests.get("https://watchnebula.com").text

    initial_state = re.search(
        '<script id="initial-app-state" type="application/json">((.|\n)*?)</script>', html_result).group(1)
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


def get_video_manifest(video_id, relogin_on_fail=True):
    response = requests.get("https://player.zype.com/manifest/" + video_id + ".m3u8",
                            headers=HEADERS_WITH_ONLY_USER_AGENT,
                            params={
                                "access_token": storage.get_zype_token(),
                                "ad_enabled": "false",
                                "https": "true",
                                "preview": "false"
                            })

    if response.status_code == 401:
        login()
        return _get_video_manifest(video_id, relogin_on_fail=False)

    response.raise_for_status()

    lines = response.text.splitlines()
    playlist_entries = []
    for i in range(1, len(lines) - 1):
        playlist_entries.append((lines[i], lines[i + 1]))

    return playlist_entries


def get_categories():
    categories = [(k, v) for k, v in _get_channel_list()["categories"]
                  ["byTitle"].items() if (k[0] != "_" and k != "YouTube Channel")]
    categories.sort(key=lambda a: a[0])

    return categories


def get_channels_in_category(category_title):
    channels = [v for k, v in _get_channel_list()["channels"]
                ["byID"].items() if v["genre"] == category_title]
    channels.sort(key=lambda a: a["title"])

    return channels


def get_channel_by_id(id):
    return _get_channel_list()["channels"]["byID"][id]


def get_all_channels():
    channels = [v for k, v in _get_channel_list()["channels"]["byID"].items()]
    channels.sort(key=lambda a: a["title"])

    return channels


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

import xbmcaddon
import json
import datetime
import time
import xbmc

_addon = xbmcaddon.Addon()

def _get_channel_cache_file_name():
    return xbmc.translatePath(_addon.getAddonInfo("profile") + "channels_v2.json")


def is_logged_in():
    return True


def get_saved_username():
    return _addon.getSettingString("username")


def get_saved_password():
    return _addon.getSettingString("password")


def get_setting_max_vertical_resolution():
    resolutions = [480, 720, 1080, 2160, 999999]
    return resolutions[_addon.getSettingInt("resolution")]


def get_nebula_token():
    return _addon.getSetting("nebula_token")

def set_nebula_token(token):
    _addon.setSetting("nebula_token", token)

def get_zype_token():
    return _addon.getSetting("zype_token")

def set_zype_token(token):
    _addon.setSetting("zype_token", token)

def get_last_cache_date():
    """
    Returns unix time of last channel cache date or -1 if no channel was cached yet
    """
    setting = _addon.getSetting("last_cache_date_v2")
    if len(setting) == 0:
        return -1

    return int(setting)


def get_cached_channels():
    with open(_get_channel_cache_file_name(), "r") as f:
        return json.load(f)


def save_cached_channels(channels):
    with open(_get_channel_cache_file_name(), "w") as f:
        json.dump(channels, f)
    _addon.setSetting("last_cache_date_v2", str(int(time.mktime(datetime.datetime.now().timetuple()))))
import sys
from urllib import urlencode
from urlparse import parse_qsl
import xbmcgui
import xbmc
import xbmcplugin
import requests
import xbmcaddon

from nebulalib import api, storage

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_url, urlencode(kwargs))


def get_channel_list_item(channel):
    xbmc.log(str(channel), xbmc.LOGNOTICE)
    list_item = xbmcgui.ListItem(label=channel["title"])
    list_item.setProperty("IsPlayable", "false")

    list_item.setArt({
        "thumb": channel["avatar"],
        "icon": channel["avatar"],
        "fanart": channel["banner"]
    })

    list_item.setInfo("video", {
        "tagline": channel["bio"],
        "plotoutline": channel["bio"],
        "title": channel["title"]
    })

    return list_item


def display_global_category_list():
    categories = api.get_categories()

    xbmcplugin.setPluginCategory(_handle, "Categories")
    xbmcplugin.setContent(_handle, "videos")

    for category in categories:
        title = category[0]

        list_item = xbmcgui.ListItem(label=title)
        list_item.setProperty("IsPlayable", "false")

        url = get_url(action='category', title=title)

        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    xbmcplugin.endOfDirectory(_handle)


def display_category(title):
    xbmc.log(str(), xbmc.LOGNOTICE)

    channels = api.get_channels_in_category(title)

    xbmcplugin.setPluginCategory(_handle, "Category")
    xbmcplugin.setContent(_handle, "videos")

    for channel in channels:
        list_item = get_channel_list_item(channel)
        url = get_url(action="channel", title=channel["_id"])

        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    xbmcplugin.endOfDirectory(_handle)


def router(params):
    if storage.get_nebula_token() is None:
        api.login()

    action = params.get("action")

    if action == "category":
        display_category(params["title"])
    else:
        display_global_category_list()


if __name__ == '__main__':
    try:
        router(dict(parse_qsl(sys.argv[2][1:])))
    except api.InvalidCredentials as e:
        xbmcgui.Dialog().ok("Login Error",
                            "Failed to login to Nebula. Make sure you entered valid e-mail and password in Addon Settings")

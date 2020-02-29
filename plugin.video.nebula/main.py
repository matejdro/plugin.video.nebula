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

def display_global_category_list():
    categories = api.get_categories()

    xbmcplugin.setPluginCategory(_handle, "Categories")
    xbmcplugin.setContent(_handle, "videos")

    for category in categories:
        title = category[0]
        category_id = categories[1]

        list_item = xbmcgui.ListItem(label=title)
        list_item.setInfo("video", {"mediatype": "video"})
        list_item.setProperty("IsPlayable", "false")

        url = get_url(action='category', id=category_id)

        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    xbmcplugin.endOfDirectory(_handle)
        


def router():
    if storage.get_nebula_token() is None:
        api.login()
    
    display_global_category_list()

if __name__ == '__main__':
    try:
        router()
    except api.InvalidCredentials as e:
        xbmcgui.Dialog().ok("Login Error", "Failed to login to Nebula. Make sure you entered valid e-mail and password in Addon Settings")
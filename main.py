import sys
from urllib import urlencode
from urlparse import parse_qsl
import xbmcgui
import xbmc
import xbmcplugin
import requests
import xbmcaddon

from nebulalib import api, storage, videos

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


def create_channel_list_item(channel):
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

def create_video_list_item(video):
    list_item = xbmcgui.ListItem(label=video["title"])
    list_item.setProperty("IsPlayable", "true")

    image = video["thumbnails"][0]["url"]

    list_item.setArt({
        "thumb": image,
        "icon": image
    })

    list_item.setInfo("video", {
        "duration": video["duration"],
        "tagline": video["description"],
        "plotoutline": video["description"],
        "title": video["title"],
        "mediatype": "video"
    })

    return list_item


def display_global_category_list():
    categories = api.get_categories()

    xbmcplugin.setPluginCategory(_handle, "Categories")
    xbmcplugin.setContent(_handle, "videos")

    all_list_item = xbmcgui.ListItem(label="All Channels")
    all_list_item.setProperty("IsPlayable", "false")
    url = get_url(action='all_channels')
    xbmcplugin.addDirectoryItem(_handle, url, all_list_item, True)

    search_list_item = xbmcgui.ListItem(label="Search")
    search_list_item.setProperty("IsPlayable", "false")
    url = get_url(action='start_search')
    xbmcplugin.addDirectoryItem(_handle, url, search_list_item, True)

    for category in categories:
        title = category[0]

        list_item = xbmcgui.ListItem(label=title)
        list_item.setProperty("IsPlayable", "false")

        url = get_url(action='category', title=title)

        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    xbmcplugin.endOfDirectory(_handle)

def display_all_channels():
    channels = api.get_all_channels()

    xbmcplugin.setPluginCategory(_handle, "Category")
    xbmcplugin.setContent(_handle, "videos")

    for channel in channels:
        list_item = create_channel_list_item(channel)
        url = get_url(action="channel", id=channel["_id"])

        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    xbmcplugin.endOfDirectory(_handle)

def display_category(title):
    channels = api.get_channels_in_category(title)

    xbmcplugin.setPluginCategory(_handle, "Category")
    xbmcplugin.setContent(_handle, "videos")

    for channel in channels:
        list_item = create_channel_list_item(channel)
        url = get_url(action="channel", id=channel["_id"])

        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    xbmcplugin.endOfDirectory(_handle)

def display_channel_videos(channel_id, page):
    videos = api.get_channel_videos(api.get_channel_by_id(channel_id), page)

    xbmcplugin.setPluginCategory(_handle, "Category")
    xbmcplugin.setContent(_handle, "videos")

    if page > 1:
        prev_page_list_item = xbmcgui.ListItem(label="<< Previous Page")
        prev_page_list_item.setProperty("IsPlayable", "false")

        url = get_url(action='channel', id = channel_id, page = page - 1)
        xbmcplugin.addDirectoryItem(_handle, url, prev_page_list_item, True)

    for video in videos:
        list_item = create_video_list_item(video)
        url = get_url(action="video", id=video["_id"])

        xbmcplugin.addDirectoryItem(_handle, url, list_item, False)

    if len(videos) >= 20:
        next_page_list_item = xbmcgui.ListItem(label="Next Page >>")
        next_page_list_item.setProperty("IsPlayable", "false")

        url = get_url(action='channel', id = channel_id, page = page + 1)
        xbmcplugin.addDirectoryItem(_handle, url, next_page_list_item, True)

    xbmcplugin.endOfDirectory(_handle)

def play_video(id):
    url = videos.get_video_url(id)
    play_item = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(_handle, True, play_item)

def start_search():
    keyword = xbmcgui.Dialog().input("Search")
    if keyword == None or keyword == "":
        return

    videos = api.search(keyword)

    xbmcplugin.setPluginCategory(_handle, "Category")
    xbmcplugin.setContent(_handle, "videos")

    if len(videos) == 0:
        no_results_list_item = xbmcgui.ListItem(label="No Results")
        no_results_list_item.setProperty("IsPlayable", "false")

        url = get_url(action='home')
        xbmcplugin.addDirectoryItem(_handle, url, no_results_list_item, True)
    else:
        for video in videos:
            list_item = create_video_list_item(video)
            url = get_url(action="video", id=video["_id"])

            xbmcplugin.addDirectoryItem(_handle, url, list_item, False)

    xbmcplugin.endOfDirectory(_handle)

def router(params):
    if storage.get_nebula_token() == "" or storage.get_zype_token() == "":
        api.login()
    action = params.get("action")

    if action == "category":
        display_category(params["title"])
    if action == "channel":
        display_channel_videos(params["id"], int(params.get("page") or 1))
    elif action == "all_channels":
        display_all_channels()
    elif action == "video":
        play_video(params["id"])
    elif action == "start_search":
        start_search()
    else:
        display_global_category_list()


if __name__ == '__main__':
    try:
        router(dict(parse_qsl(sys.argv[2][1:])))
    except api.InvalidCredentials as e:
        xbmcgui.Dialog().ok("Login Error",
                            "Failed to login to Nebula. Make sure you entered valid e-mail and password in Addon Settings")

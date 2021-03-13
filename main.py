import sys
import urllib
import xbmcgui
import xbmc
import xbmcplugin
import requests
import xbmcaddon

from nebulalib import api, storage, videos, lists
from nebulalib.util import get_url

# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])


def display_global_category_list():
    categories = api.get_categories()

    xbmcplugin.setPluginCategory(_handle, "Categories")
    xbmcplugin.setContent(_handle, "videos")

    all_list_item = xbmcgui.ListItem(label="All Channels")
    all_list_item.setProperty("IsPlayable", "false")
    url = get_url(action='all_channels')
    xbmcplugin.addDirectoryItem(_handle, url, all_list_item, True)

    all_videos_item = xbmcgui.ListItem(label="All Videos")
    all_videos_item.setProperty("IsPlayable", "false")
    url = get_url(action='all_videos')
    xbmcplugin.addDirectoryItem(_handle, url, all_videos_item, True)

    search_list_item = xbmcgui.ListItem(label="Search")
    search_list_item.setProperty("IsPlayable", "false")
    url = get_url(action='start_search')
    xbmcplugin.addDirectoryItem(_handle, url, search_list_item, True)

    lists.show_category_list(_handle, categories)

    xbmcplugin.endOfDirectory(_handle)

def display_all_channels():
    channels = api.get_all_channels()

    xbmcplugin.setPluginCategory(_handle, "Category")
    xbmcplugin.setContent(_handle, "videos")

    lists.show_channel_list(_handle, channels)

    xbmcplugin.endOfDirectory(_handle)

def display_category(title):
    channels = api.get_channels_in_category(title)

    xbmcplugin.setPluginCategory(_handle, "Category")
    xbmcplugin.setContent(_handle, "videos")

    lists.show_channel_list(_handle, channels)

    xbmcplugin.endOfDirectory(_handle)

def display_all_videos(page):
    videos = api.get_all_videos(page)

    xbmcplugin.setPluginCategory(_handle, "Category")
    xbmcplugin.setContent(_handle, "videos")

    if page > 1:
        prev_page_list_item = xbmcgui.ListItem(label="<< Previous Page")
        prev_page_list_item.setProperty("IsPlayable", "false")

        url = get_url(action='all_videos', page = page - 1)
        xbmcplugin.addDirectoryItem(_handle, url, prev_page_list_item, True)

    lists.show_video_list(_handle, videos)

    if len(videos) >= 20:
        next_page_list_item = xbmcgui.ListItem(label="Next Page >>")
        next_page_list_item.setProperty("IsPlayable", "false")

        url = get_url(action='all_videos', page = page + 1)
        xbmcplugin.addDirectoryItem(_handle, url, next_page_list_item, True)

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

    lists.show_video_list(_handle, videos)

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
        lists.show_video_list(_handle, videos)

    xbmcplugin.endOfDirectory(_handle)

def router(params):
    if storage.get_nebula_token() == "" or storage.get_zype_token() == "":
        api.login()
    action = params.get("action")

    if action == "category":
        display_category(params["title"])
    if action == "channel":
        display_channel_videos(params["id"], int(params.get("page") or 1))
    elif action == "all_videos":
        display_all_videos(int(params.get("page") or 1))
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
        router(dict(urllib.parse.parse_qsl(sys.argv[2][1:])))
    except api.InvalidCredentials as e:
        xbmcgui.Dialog().ok("Login Error",
                            "Failed to login to Nebula. Make sure you entered valid e-mail and password in Addon Settings")

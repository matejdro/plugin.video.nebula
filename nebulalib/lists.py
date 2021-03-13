import xbmc
import xbmcplugin
import xbmcgui

from .util import get_url

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

def show_category_list(handle, categories):
    for category in categories:
        list_item = xbmcgui.ListItem(label=category)
        list_item.setProperty("IsPlayable", "false")

        url = get_url(action='category', title=category)

        xbmcplugin.addDirectoryItem(handle, url, list_item, True)

def show_channel_list(handle, channels):
    for channel in channels:
        list_item = create_channel_list_item(channel)
        url = get_url(action="channel", id=channel["_id"])

        xbmcplugin.addDirectoryItem(handle, url, list_item, True)

def show_video_list(handle, videos):
    for video in videos:
        list_item = create_video_list_item(video)
        url = get_url(action="video", id=video["_id"])

        xbmcplugin.addDirectoryItem(handle, url, list_item, False)
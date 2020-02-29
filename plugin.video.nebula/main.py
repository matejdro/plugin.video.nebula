import sys
from urllib import urlencode
from urlparse import parse_qsl
import xbmcgui
import xbmcplugin
import requests
import xbmcaddon

from nebulalib import api, storage

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

def router():
    api.login()

if __name__ == '__main__':
    try:
        router()
    except api.InvalidCredentials as e:
        xbmcgui.Dialog().ok("Login Error", "Failed to login to Nebula. Make sure you entered valid e-mail and password in Addon Settings")
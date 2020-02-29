import xbmcaddon

_addon = xbmcaddon.Addon()


def is_logged_in():
    return True

def get_saved_username():
    return _addon.getSettingString("username")

def get_saved_password():
    return _addon.getSettingString("password")

def get_setting_max_vertical_resolution():
    resolutions = [720, 1080, 2160, 999999]
    return resolutions[_addon.getSettingInt("resolution")]

def get_nebula_token():
    return _addon.getSettingString("nebula_token")

def set_nebula_token(token):
     _addon.setSetting("nebula_token", token)
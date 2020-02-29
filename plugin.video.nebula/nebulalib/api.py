import storage
import requests
import xbmc

class InvalidCredentials(Exception):
    pass

def login():
    body = {
        "email": storage.get_saved_username(),
        "password": storage.get_saved_password()
    }

    user_data = requests.post("https://api.watchnebula.com/api/v1/auth/login/", json=body)
    if user_data.status_code != 200:
        raise InvalidCredentials()

    result_json = user_data.json()

    storage.set_nebula_token(result_json["key"])
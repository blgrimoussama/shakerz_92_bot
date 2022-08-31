import requests
from credentials import *

headers = {'Authorization': CHAT_ACCESS_TOKEN,
           'Client-Id': CLIENT_ID}

validation = requests.get(
    'https://id.twitch.tv/oauth2/validate', headers=headers).json()
print(validation)

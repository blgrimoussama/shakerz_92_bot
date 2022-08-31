from requests import Request
from credentials import *

# obtain access token
url = "https://id.twitch.tv/oauth2/authorize"


data = {
    "response_type": "token",
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "scope": 'chat:edit chat:read',
}

response = Request("GET", url, params=data).prepare()

print(f'\n{response.url}')

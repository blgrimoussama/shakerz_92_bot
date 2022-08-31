from requests import Request
from credentials import *
import webbrowser

# obtain access token
url = "https://id.twitch.tv/oauth2/authorize"

scopes = ['bits:read',
          'chat:read',
          'chat:edit',
          'channel:read:redemptions',
          'channel:read:hype_train',
          'channel:manage:redemptions',
          'channel:read:subscriptions',
          'channel:manage:predictions',
          'channel:read:predictions'
          ]

data = {
    "response_type": "token",
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "scope": ' '.join(scopes),
}

response = Request("GET", url, params=data).prepare()

webbrowser.open(response.url)

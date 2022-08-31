from credentials import *
import requests

url = "https://id.twitch.tv/oauth2/token"


data = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": "client_credentials",
}

response = requests.post(url, params=data)

with open('.env', "a") as env:
    env.write(f"\nexport API_ACCESS_TOKEN = {response.json()['access_token']}")

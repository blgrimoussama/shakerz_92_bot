from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
CHAT_ACCESS_TOKEN = os.getenv('CHAT_ACCESS_TOKEN')
my_token = os.getenv('CHAT_ACCESS_TOKEN')
CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
shakerz_92_CHANNEL_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
API_ACCESS_TOKEN = os.getenv('API_ACCESS_TOKEN')
import os

BOT_TOKEN = os.getenv('AO3TIME_BOT_TOKEN', '')
ALLOWED_USERS = set(map(int, filter(None, os.getenv('AO3TIME_ALLOWED_USERS', '').split(','))))

import os
from dotenv import load_dotenv #библиотека для парсинга .env файла

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN') #должно быть в файле .env
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(',')))#должно быть в файле .env
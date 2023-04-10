import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import openai
import configparser
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
from pymongo import MongoClient
import datetime
import os


config = configparser.ConfigParser()
config.read('config.ini')

openai.api_key = os.environ["OPENAI"]
youtube_api_key = os.environ["YOUTUBE"]
trans_api_key = os.environ["TRANSKEY"]
trans_api_host = os.environ["TRANSHOST"]
trans_api_url = os.environ["TRANSURL"]
db_url = os.environ["DBURL"]

bot = telegram.Bot(token=(config['TELEGRAM']['ACCESS_TOKEN']))

youtube = build('youtube', 'v3', developerKey=youtube_api_key)


#database: MongoDB#
client = MongoClient(db_url)
db = client.chatbot
collection = db.user_commands


def insert_command(user_id, command):
    now = datetime.datetime.now()
    doc = {
        'user_id': user_id,
        'command': command,
        'timestamp': now
    }
    collection.insert_one(doc)


#Telegram ChatBot Class
class TelegramBot:
    def __init__(self):
        self.updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.add_handlers()

    def start(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Hello，I'm your education ChatBot！")
        insert_command(update.effective_chat.id, '/start')

    def search_video(self, update, context):
        keyword = " ".join(context.args)
        chat_id = update.effective_chat.id

        try:
            search_response = youtube.search().list(
                q=keyword,
                type='video',
                part='id,snippet',
                maxResults=5
            ).execute()

            for search_result in search_response.get('items', []):
                if search_result['id']['kind'] == 'youtube#video':
                    video_id = search_result['id']['videoId']
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    context.bot.send_message(chat_id=chat_id, text=video_url)

            insert_command(chat_id, '/search_video')

        except HttpError as e:
            bot.send_message(chat_id=chat_id, text=f"An error occurred: {e}")
            insert_command(chat_id, '/search_video_error')

    def chat(self,  update, context):
        user_message = update.message.text
        messages = []
        system_message = "Hi, how can I help you today?"
        messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": user_message})
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, max_tokens=100)
        bot_reply = response["choices"][0]["message"]["content"]
        update.message.reply_text(bot_reply)
        insert_command(update.effective_chat.id, '/chat')

    def translate(self, update, context):
        text_to_translate = " ".join(context.args)

        params = {"word": text_to_translate, "source_lang": "en", "dest_lang": "zh"}

        headers = {
            'X-RapidAPI-Key': trans_api_key,
            'X-RapidAPI-Host': trans_api_host
        }

        response = requests.get(trans_api_url, headers=headers, params=params)

        translation = response.text

        context.bot.send_message(chat_id=update.effective_chat.id, text=translation)
        insert_command(update.effective_chat.id, '/translate')

    def add_handlers(self):
        start_handler = CommandHandler('start', self.start)
        search_video_handler = CommandHandler('search_video', self.search_video)
        translate_handler = CommandHandler('translate', self.translate)
        chat_handler = MessageHandler(telegram.ext.Filters.text, self.chat)

        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(search_video_handler)
        self.dispatcher.add_handler(translate_handler)
        self.dispatcher.add_handler(chat_handler)

    def start_polling(self):
        self.updater.start_polling()
        self.updater.idle()


# begin to run
bot = TelegramBot()
bot.start_polling()


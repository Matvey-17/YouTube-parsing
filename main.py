import telebot
from telebot.handler_backends import State, StatesGroup
from telebot import StateMemoryStorage, custom_filters

from pytube import YouTube
import ssl

import sqlite3

from api_token import API_TOKEN

state_storage = StateMemoryStorage()

bot = telebot.TeleBot(API_TOKEN, state_storage=state_storage)


class DbConnect:
    def __init__(self, chat_id):
        self.chat_id = chat_id

    def connect(self):
        with sqlite3.connect('YouTube.db') as db:
            cursor = db.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS media(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_tg INTEGER UNIQUE,
            url TEXT
            )""")
            db.commit()
            try:
                cursor.execute(f"INSERT INTO media (id_tg) VALUES ({self.chat_id})")
                db.commit()
            except sqlite3.IntegrityError:
                cursor.execute(f"UPDATE media SET id_tg = {self.chat_id} WHERE id_tg = {self.chat_id}")
                db.commit()

    def add_url(self, name_video):
        with sqlite3.connect('YouTube.db') as db:
            cursor = db.cursor()
            cursor.execute(f"UPDATE media SET url = '{name_video}' WHERE id_tg = {self.chat_id}")
            db.commit()

    def get_url(self):
        with sqlite3.connect('YouTube.db') as db:
            cursor = db.cursor()
            cursor.execute(f"SELECT url FROM media WHERE id_tg = {self.chat_id}")
            url = cursor.fetchone()[0]
        return url


class States(StatesGroup):
    url = State()


def download(url, chat_id):
    ssl._create_default_https_context = ssl._create_unverified_context

    yt = YouTube(url)
    video = yt.streams.first().download('/Users/matveyvarlamov/cours_umschool/umschool/media')
    name_video = video

    db_add_url = DbConnect(chat_id)
    db_add_url.add_url(name_video)


@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    db_conn = DbConnect(message.chat.id)
    db_conn.connect()

    markup = telebot.types.InlineKeyboardMarkup()
    bt_start = telebot.types.InlineKeyboardButton('Начать', callback_data='ready')
    markup.add(bt_start)
    bot.send_message(message.chat.id, 'Привет! Я помогу тебе скачать видео из YouTube 📹',
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'ready')
def callback(call: telebot.types.CallbackQuery):
    bot.set_state(call.from_user.id, States.url, call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Супер! Отправь мне ссылку на видео из YouTube 📲')


@bot.message_handler(content_types=['text'], state=States.url)
def download_url(message: telebot.types.Message):
    bot.send_message(message.chat.id, 'Сейчас начнется загрузка ⚙️')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['url'] = message.text
        msg = bot.send_message(message.chat.id, '--------------------')
        download(data['url'], message.chat.id)
    bot.delete_message(message.chat.id, msg.message_id)
    bot.send_message(message.chat.id, 'Загрузка завершена 🎉 Отправляю видео 📥')
    db_get_url = DbConnect(message.chat.id)
    result = db_get_url.get_url()
    with open(f'{result}', 'rb') as video:
        bot.send_video(message.chat.id, video, caption='Держи 🎁')
    bot.delete_state(message.from_user.id, message.chat.id)


if __name__ == '__main__':
    print('Бот запущен')
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.add_custom_filter(custom_filters.IsDigitFilter())
    bot.infinity_polling()
    print('Бот остановлен')

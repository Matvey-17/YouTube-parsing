import telebot
from telebot.handler_backends import State, StatesGroup
from telebot import StateMemoryStorage, custom_filters

import re

from api_token import API_TOKEN
from DB import DbConnect
from Download import download

pattern = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'

state_storage = StateMemoryStorage()

bot = telebot.TeleBot(API_TOKEN, state_storage=state_storage)


class States(StatesGroup):
    url = State()


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
    if re.findall(pattern, message.text):
        bot.send_message(message.chat.id, 'Сейчас начнется загрузка ⚙️')

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['url'] = message.text
            msg = bot.send_message(message.chat.id, '--------------------')
            download(data['url'], message.chat.id)

        bot.delete_message(message.chat.id, msg.message_id)
        bot.send_message(message.chat.id, 'Загрузка завершена 🎉 Отправляю видео 📥')
        db_get_url = DbConnect(message.chat.id)
        result = db_get_url.get_url()

        if result != 'None':
            with open(f'{result}', 'rb') as video:
                bot.send_video(message.chat.id, video, caption='Держи 🎁')
        else:
            bot.send_message(message.chat.id, 'К сожалению, видео превышает 50 МБ - я не смогу его отправить 😔')

        bot.delete_state(message.from_user.id, message.chat.id)

    else:
        bot.send_message(message.chat.id, 'Неверная ссылка. Проверь на корректность 🔍')


@bot.message_handler(content_types=['text'])
def more_text(message: telebot.types.Message):
    bot.send_message(message.chat.id, 'Неверная команда ❌\n\nДля загрузки видео нажми кнопку "Начать"')


if __name__ == '__main__':
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.infinity_polling()

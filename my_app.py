import markovify
import re
from num2words import num2words
import telebot
import config
import flask

bot = telebot.TeleBot("936409992:AAFSFcJDTbBGEZZIeWu5KydMpvM-HdCXjCk")

def text_correction(text):
    text = text.replace('\n', '')
    text = text.replace('\r', '')
    text = text.replace('\t', '')
    text = text.replace('..', '.')
    text = text.replace('...', '.')
    text = text.replace('…', '.')
    no_tags = re.compile('<.*?>')
    text = re.sub(no_tags, '', text)
    non_words = re.compile(r'[^\.a-zA-Z0-9_\s]')
    text.lower()
    return text

def teach_model():
    with open("potter.txt", encoding="windows-1251") as f:
        text = text_correction(f.read())
    text_model = markovify.Text(text, retain_original=False, state_size=5)
    return text_model

app = flask.Flask(__name__)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'Приветствую! Я бот, который составит Вам фразу на основе марковской цепи по всем книгам о Гарри Поттере.\n Напишите в ответ какой-нибудь текст.')

@bot.message_handler(content_types=['text'])
def reply(message):
    bot.send_message(message.chat.id, 'Подождите минуту, сейчас все будет...')
    text = teach_model().make_short_sentence(140, tries=100)
    if text is None:
        text = 'Извините, что-то пошло не так, не могли бы Вы повторить?'
    user = message.chat.id
    bot.send_message(user, 'Ваша фраза:\n ' + text)

bot.polling(none_stop = True)

if __name__ == '__main__':
    import os
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

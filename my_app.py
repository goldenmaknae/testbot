import markovify
import re
from num2words import num2words
import telebot
import config
import flask
import os
TOKEN = os.environ["TOKEN"]

bot = telebot.TeleBot("956616668:AAFvXQ3CJZXE644ZmzTYQNRnm2ko4Uao0kY")

telebot.apihelper.proxy = {'https': 'socks5h://geek:socks@t.geekclass.ru:7777'}


# модуль для форматирования текста в облегченный и более правильный
# вид для обучения модели
def correct_text(text):
    # компиляция регулярных выражений для поиска при загрузке пользователем
    # более одного документа для создания модели
    # TODO расположил в порядке применения
    text = text.replace('\n', '')
    text = text.replace('\r', '')
    text = text.replace('\t', '')
    text = text.replace('..', '.')
    text = text.replace('...', '.')
    text = text.replace('…', '.')
    no_tags = re.compile('<.*?>')
    text = re.sub(no_tags, '', text)
    # перевод цифр и чисел из знаков в текстовый формат, таким образом
    # модель будет адекватнее обучена на употребление числительных
    # text = re.sub(r'(\d*\.\d+|\d+)', num2words('\1', lang='ru'), text)
    # находит дурацкие символы буееее
    non_words = re.compile(r'[^\.a-zA-Z0-9_\s]')
    # text = non_words.sub('', text)
    # понижение регистра во всем тексте, чтобы убрать разделение одинаковых
    # слов по размеру букв - оптимизация объема словаря
    text.lower()
    return text


# основной модуль программы. обучает отредактированную модель.
def open_file_to_model():
    # перевод "сырого" текста в строку и корректирование
    with open("potter.txt", encoding="windows-1251") as f:
        text = correct_text(f.read())
    # определяем размер файла для выбора оптимального окна из расчета, что
    # num_different_words_in_corpus^num_look_back_words =
    # = размер таблицы вероятности.
    # state_size = len(text)  # TODO рздлть на k, округлить
    # построение модели
    text_model = markovify.Text(text, retain_original=False,
                                state_size=5)
    # TODO сделать поттера в джсоне и подгружать оттудда
    return text_model


bot.remove_webhook()
bot.set_webhook(url="https://harrybotr.herokuapp.com/bot")
app = flask.Flask(__name__)


# привет всем говорит бот
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):

    bot.send_message(message.chat.id, 'Привет! Я пришлю вам предложение '
                                      'сгенерированное с помощью машинного '
                                      'обучения по всем книгам о Гарри '
                                      'Поттере,'
                                      ' если вы отправите мне текст')
    bot.send_message(message.chat.id, 'Отправьте мне любое '
                                      'текстовое сообщение')


# это нужно для отлова неправильного формата контента от пользователя,
# отлавливаю его, чтобы в дальнейшем сделать возможность
# подгрузки документа от пользователя.
@bot.message_handler(func=lambda m: True,
                     content_types=['audio, document, sticker, photo, video'])
def send_question(message):
    bot.reply_to(message, 'Пожалуйста, отправьте текст, '
                          'это же не текст, что вы отправили')


@bot.message_handler(content_types=['text'])
def reply(message):
    bot.send_message(message.chat.id, 'Так, сообщение получил, работаю. '
                                      'Скоро отправлю предложение, '
                                      'подождите, пожалуйста.')
    text = open_file_to_model().make_short_sentence(140, tries=100)
    if text is None:
        text = 'Упс, у меня что-то не получилось придумать ' \
               'предложение, попробуйте еще разок'
    user = message.chat.id
    bot.send_message(user, 'Прошу, ваше предложение:\n ' + text)


# Лиза Леонова очень мило поделилась со мной скриптом,
# который позволяет хостить на хероку через вебхуки и не переживать:
@app.route("/", methods=['GET', 'HEAD'])
def index():
    return 'ok'


@app.route("/bot", methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        # written with help from Ivan Torubarov
        try:
            webhook_info = bot.get_webhook_info()
            if webhook_info.pending_update_count > 1:
                print('Evaded unwanted updates: ',
                      str(webhook_info.pending_update_count))
                return ''
            else:
                print('Updating')
                bot.process_new_updates([update])
        except Exception as e:
            print('%s occured' % str(e))
            pass
        return ''
    else:
        flask.abort(403)

bot.polling(none_stop = True)

if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

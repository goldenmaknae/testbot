import flask
import telebot
import os

TOKEN = os.environ["TOKEN"]

bot = telebot.TeleBot(TOKEN, threaded=False)

telebot.apihelper.proxy = {'https': 'socks5h://geek:socks@t.geekclass.ru:7777'}

bot.set_webhook(url="https://<my-hp-app.herokuapp.com/bot")

app = flask.Flask(__name__)

def teach_model():
	with open("potter.txt", encoding="windows-1251") as f:
		text = f.read()
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
		text_model = markovify.Text(text, retain_original=False, state_size=5)
		return text
		return text_model        

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'Приветствую! Я бот, и я сгенерирую Вам фразу с помощью марковской цепи по всем книгам о Гарри Поттере.')
    bot.send_message(message.chat.id, 'Напишите в ответ любой текст.')

@bot.message_handler(func=lambda m: True)
def send_question(message):
    bot.send_message(message.chat.id, 'Подождите немного, сейчас все будет...')
    text = teach_model().make_short_sentence(140, tries=100)
    if text is None:
        text = 'Простите, что-то пошло не так. Не могли бы Вы попробовать еще раз?'
    user = message.chat.id
    bot.send_message(user, 'Ваша фраза:\n ' + text)

@app.route("/", methods=['GET', 'HEAD'])
def index():
    return 'ok'

@app.route("/bot", methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
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

if __name__ == '__main__':
    import os
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

from flask import Flask
from flask import request
from flask import jsonify
import telegram
#from flask_sslify import SSLify
import requests
import json
import re
URL='https://api.telegram.org/bot900723490:AAHeFy4UMUD-wHMDMG3fabQqt8iNt65ADtM/'
HOST = '116.203.132.117'
TOKEN = '900723490:AAHeFy4UMUD-wHMDMG3fabQqt8iNt65ADtM'
app = Flask(__name__)
bot = telegram.Bot(token=TOKEN)
def load_requests(source_url, sink_path,chat_id):
    with open(sink_path, 'wb') as handle:
        with open(sink_path, 'wb') as handle:
            try:
                response = requests.get(source_url, stream=True)
                response.raise_for_status()
            except requests.exceptions.HTTPError:  # This is the correct syntax
                print ("HTTPError")
                return False
            except requests.exceptions.Timeout:
                print("Timeout")# Maybe set up for a retry, or continue in a retry loop
                return False
            except requests.exceptions.TooManyRedirects:
                print("TooManyRedirects")# Tell the user their URL was bad and try a different one
                return False
            except requests.exceptions.ConnectionError:
                print("ConnectionError")
                return False
            except requests.exceptions.RequestException as e:

        # catastrophic error. bail.
                print ("True error is :", e)
                return False
            else:
                for block in response.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)
                return True


            # load_requests("http://www.meteoinfo.by/radar/UKBB/radar-map.gif","Meteo.gif")



def removeCustomKeyboard(chat_id):
    print("Removing custom Keyboard")
    url=URL + 'sendMessage'
    reply_markup = {'remove_keyboard':True}
    answer = {'chat_id': chat_id,'text':"...",'reply_markup': reply_markup}
    r = requests.post(url, json = answer )

def sendInlineKeyBoard(chat_id):
    print("InlineFunct!!!!")
    url=URL + 'sendMessage'
    reply_markup = {'inline_keyboard': [[{'text': 'Weather','callback_data':'weather'}], [{'text': 'TalkToMe','callback_data':'text'}]]}
    answer = {'chat_id': chat_id, 'text': "Hello!", 'reply_markup': reply_markup}
    r = requests.post(url,json=answer)
    write_json(r.json())


def sendLocation_Contact(chat_id):


    reply_markup= {'keyboard': [[{'text': 'Send location','request_location':True}], [{'text': 'Send Phone Number','request_contact':True}]],
                   'resize_keyboard': True,
                   'one_time_keyboard': True
                    }
    # data = {'chat_id': chat_id, 'text':' ', 'reply_markup': reply_markup}
    url=URL + 'sendMessage'

    answer = {'chat_id': chat_id, 'text': "AAA", 'reply_markup': reply_markup}
    #print("Location answer:",answer)
    r = requests.post(url,json=answer)
    return r.json()

def sendCurrency(chat_id):
    reply_markup= {'keyboard': [[{'text': 'USD'}], [{'text': 'EUR'}],[{'text': 'RUR'}],[{'text':'BTC'}]],
                   'resize_keyboard': True,
                   'one_time_keyboard': True
                    }
    # data = {'chat_id': chat_id, 'text':' ', 'reply_markup': reply_markup}
    url=URL + 'sendMessage'

    answer = {'chat_id': chat_id, 'text': "Please choose currency!", 'reply_markup': reply_markup}
    #print("Location answer:",answer)
    r = requests.post(url,json=answer)
    return r.json()

def write_json(data, filename='answer.json'):
    with open(filename,'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_updates():
    print("Get update")
    url = URL + 'getUpdates'
    r = requests.get(url)
    #write_json(r.json())
    return r.json()

def send_message(chat_id,text='bla-bla-bla',reply_m = ''):
    url=URL + 'sendMessage'
    answer = {'chat_id': chat_id, 'text': text,'reply_markup':reply_m}
    r = requests.post(url,json=answer)
    return r.json()

def send_photo(chat_id, text = 'Weather'):
    print("Weather handler!")
    url=URL + 'sendVideo'
    if load_requests("http://www.meteoinfo.by/radar/UKBB/radar-map.gif","Meteo.gif",chat_id) is False:
        send_message(chat_id,text = "We are sorry, but now service is not available.")
    else:
        answer = {'chat_id': chat_id, 'supports_streaming':True, 'caption':"Here you go!"}
        files = {'video': open('Meteo.gif', 'rb')}
        r = requests.post(url,params = answer,files = files)
        return r.json()


def parse_text(text):
    pattern = r'/\w+'
    crypto = re.search(pattern, text).group()
    return crypto[1:]

def get_exchange(crypto):
    url = 'https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5'
    r = requests.get(url)
    r = r.json()

    for currency in r:
        print(currency.values())
        if currency['ccy']==crypto:
            print("success, buy:",currency['buy'])
            price = {'buy':currency['buy'],'sale':currency['sale']}

    write_json(r, filename = 'price.json')
    return price


def get_price(crypto):
    url = 'https://api.coinmarketcap.com/v1/ticker/{}'.format(crypto)
    r = requests.get(url)
    if not r.ok:
        print("Smth fucked up us")
        price = "None such crypto"
    else:
        r = r.json()
        price = r[-1]['price_usd']
        write_json(r, filename = 'price.json')
    return price

@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'Yo you telefuck'


@app.route(f'/{TOKEN}', methods=['POST','GET'])
#def index():
def getMessage():
    if request.method == 'POST':
        print("POST method!")
        r = request.get_json()
        write_json(r)
        print("response: ",r)

        chat_id = ''
        message = ''
        longitude = ''
        latitude = ''
        currList = ['USD','EUR','RUR','BTC']
        dictFunct = {'weather':send_photo, 'text':send_message}

        if 'callback_query' in r:
            chat_id = r['callback_query']['message']['chat']['id']
            print("callback_data = ", r['callback_query']['data'])
            callback_data = r['callback_query']['data']
            dictFunct[callback_data](chat_id,text="I dont want to!")

            return jsonify(result={"status": 200})
        elif 'edited_message' in r:
            print("Edited")
        elif 'contact' in r['message']:
            print("Contact have been reached")
            chat_id = r['message']['chat']['id']
            phone = r['message']['contact']['phone_number']
            print('Phone Number is:',phone)
            removeCustomKeyboard(chat_id)
            return jsonify(result={"status": 200})
        elif 'location' in r['message']:
            print("Location have been reached")
            chat_id = r['message']['chat']['id']
            latitude = r['message']['location']['latitude']
            longitude = r['message']['location']['longitude']
            print('latitude:{}, longitude:{}'.format(latitude,longitude))
            removeCustomKeyboard(chat_id)
            return jsonify(result={"status": 200})
        # elif 'data' in r['callback_query']:
        #     print("CallbackId is:", r['callback_query']['data'])
        elif 'animation' in r['message']:
            print("This is ani message")
        elif 'voice' in r['message']:
            print("Voice!")
        else:
            chat_id = r['message']['chat']['id']
            message = r['message']['text']
            print ("Text: ",message)

        # phone = r['contact']['phone_number']

        # print("Phone: ",phone)
        pattern = r'/\w+'
        # chat_id = r['message']['chat']['id']
        for current in currList:
            if current == message.upper():
                price = get_exchange(current)
                print(price['buy'],price['sale'])
                reply_markup = {'remove_keyboard':True}
                send_message(chat_id,text = 'Покупка: {}, Продажа: {} '.format(price['buy'],price['sale']),reply_m = reply_markup)
                # removeCustomKeyboard(chat_id)
                break
        if 'inline' in message.lower():
            print('Inline Request')
            sendInlineKeyBoard(chat_id)


        if 'Keyboard' in message.capitalize():
            chat_id = r['message']['chat']['id']
            print("Location request")
            sendLocation_Contact(chat_id)

        if 'Weather' in message.capitalize():
            chat_id = r['message']['chat']['id']
            send_photo(chat_id)
            write_json(r)
    #     #
        if re.search(pattern, message):
            chat_id = r['message']['chat']['id']
            crypto = parse_text(message)
            if 'weather' in  crypto.lower():
                send_photo(chat_id)
            elif 'currency' in crypto.lower():
                sendCurrency(chat_id)
            else:
            #send_message(chat_id,text = message)
            #send_photo(chat_id)
                price = get_price(crypto)
            # price = get_price("bitcoin")
            #print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Price is - ",price)
                send_message(chat_id,text = price)
                write_json(r)
            #print(jsonify(r))
            #message.clear()
            print("Returned response: ",jsonify(r))
            return jsonify(result={"status": 200})
    return '<h1>Bot Welcomes you!</h1>'
@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook(f'https://{HOST}:8443/{TOKEN}', certificate=open('/etc/ssl/despise/server.crt', 'rb'))
    if s:
        print(s)
        return "webhook setup ok"
    else:
        return "webhook setup failed"
@app.route('/delete_webhook', methods=['GET', 'POST'])
def delete_webhook():
    s = bot.deleteWebhook()
    if s:
        print(s)
        return "webhook deleted ok"
    else:
        return "webhook delete failed"
# def main():
#     print("before")
#     r = get_updates()
#     chat_id = r['result'][-1]['message']['chat']['id']
#     print(chat_id)
#     send_photo(chat_id)

#https://api.telegram.org/bot989822911:900723490:AAHeFy4UMUD-wHMDMG3fabQqt8iNt65ADtM/setWebhook?url=https://03d5da3c.ngrok.io

if __name__ == '__main__':

    app.run()
    #main()

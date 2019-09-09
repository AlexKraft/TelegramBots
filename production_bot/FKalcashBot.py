# -*- coding: utf-8 -*-
import telebot
import json
import random
import re

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

data = "datastore.json"
API_TOKEN = '750042395:AAEIWfleAt9JE-JeNIznYEdK70RfasKpXec'  # production

bot = telebot.TeleBot(API_TOKEN)


def loadDB():
    with open(data, 'r', encoding='utf-8', errors='ignore') as f:  # 
        db = json.load(f)
    return db


def uploadDB(db):
    with open(data, 'w+', encoding='utf-8', errors='ignore') as f:  # , encoding='utf-8'
        json.dump(db, f, indent=2, ensure_ascii=False)


def gen_markup(db, key=None, ch_id=None):

    markup = InlineKeyboardMarkup()

    if key == 'admin_buttons':
        if not db['game']['active']:
            markup.add(InlineKeyboardButton('Редактировать пост',
                                            callback_data='edit_game'))
            markup.add(InlineKeyboardButton('Постим?', callback_data='post'))
        else:
            markup.add(InlineKeyboardButton('Добавить игрока',
                                            callback_data='add'))
            markup.add(InlineKeyboardButton('Поделить на команды',
                                            callback_data='shuffle'))
            markup.add(InlineKeyboardButton('Отменить игру',
                                            callback_data='del'))

        markup.add(InlineKeyboardButton('Рассылка', callback_data='spam'))

    elif key == 'new_player':

        if not db['game']['active']:
            return None
        elif ch_id not in db["game"]["players"]:
            markup.add(InlineKeyboardButton('Зарегистрироваться на игру',
                                            callback_data='reg'))
        else:
            return None

    elif key == 'statistics':
        for k in db['game']["players"]:
            markup.add(InlineKeyboardButton(f"Гол: {db['players'][k]['fname']}",
                                            callback_data=k))

        markup.add(InlineKeyboardButton('Конец игры', callback_data='end'))

    return markup


@bot.message_handler(commands=['start'])
def command_start(m):
    ch_id = str(m.chat.id)
    msg_id = m.message_id

    db = loadDB()
    users = db['players']

    if ch_id in users:

        if ch_id in db["admins"]:
            markup = gen_markup(db, 'admin_buttons', ch_id)
            msg = db['game']['text_list']

            if db['game']['active'] and ch_id in db['game']['players']:
                db['game']['players'][ch_id] = msg_id + 1
        else:
            markup = gen_markup(db, 'new_player')
            msg = db['game']['text_list'] if db['game']['active'] else "пока что нет активных игр"

    else:
        msg = "Привет, у тебя должен быть секретный код для того что б пользоваться этим ботом\nПо всем вопросам пиши в группу ФБ https://www.facebook.com/groups/fkalcash/"
        markup = None
        bot.send_message(383621032,
                         f'Кто-то стучится -> {m.chat.first_name} @{m.chat.username}')

    bot.send_message(chat_id=ch_id,
                     text=msg,
                     reply_markup=markup)

    uploadDB(db)


@bot.callback_query_handler(func=lambda call: re.match('\d{9}', call.data))
def get_game_stat(call):
    who = call.data
    db = loadDB()
    players = db['game']['players']
    players[who] += 1
    uploadDB(db)


handle = ['post', 'reg', 'shuffle', 'del', 'end']
@bot.callback_query_handler(func=lambda call: call.data in handle)
def callback_func_p(call):
    ch_id = str(call.message.chat.id)
    msg_id = str(call.message.message_id)

    db = loadDB()
    players = db['players']
    game = db['game']


#                                                              >>>>>>>>>  POST

    if call.data == "post":
        game['active'] = True
        bot.delete_message(ch_id, msg_id)

        for n in players:
            r = bot.send_message(chat_id=n,
                                 text=game['text_list'],
                                 reply_markup=gen_markup(db, 'new_player', n))
            players[n]['m_id'] = r.message_id
#
#                                                               >>>>>>>>>  REG
#
    elif call.data == "reg":
        if game["active"]:
            if ch_id not in game["players"]:
                game["players"].setdefault(ch_id, msg_id)
#                players[ch_id]["ingames"] += 1
                game['list'].append(players[ch_id]["fname"])
#                print ("'reg' <<<<<<<<<<<<<<<<<<<<<<<")
                game['text_list'] = form_list(game, players)

                for player_id, msg_id in game["players"].items():
                    bot.edit_message_text(text=game['text_list'],
                                          chat_id=player_id,
                                          message_id=msg_id)

                db['game'] = game
            else:
                bot.send_message(chat_id=ch_id,
                                 text="Вы уже зарегистрированы")
        else:
            bot.delete_message(ch_id, call.message.message_id)
            command_start(call.message)
# '''
#                                                            >>>>>>>>>  SHUFLE
# '''
    elif call.data == "shuffle":
        game["text_list"] = form_teams()
        game['active'] = False

        for player_id in players:

            if player_id in game["players"]:
                if player_id in db["admins"]:
                    bot.edit_message_text(text=game["text_list"],
                                          chat_id=player_id,
                                          message_id=msg_id,
                                          reply_markup=gen_markup(db, 'statistics'))
                else:
                    bot.edit_message_text(text=game["text_list"],
                                          chat_id=player_id,
                                          message_id=msg_id)

            else:
                bot.edit_message_text(text='*Вы пропустили эту игру* \n',
                                      chat_id=player_id,
                                      message_id=players[player_id]['m_id'],
                                      parse_mode="Markdown")

            game["players"][player_id] = 0

# '''
#                                                                >>>>>>>>>  END
# '''
    elif call.data == "end":
        results = "В этой игре отметились забив:"
        bot.edit_message_reply_markup(chat_id=ch_id,
                                      message_id=msg_id)

        sorted_x = sorted(game["players"].items(), key=lambda kv: -kv[1])

        for player_id, scores in sorted_x:
            if scores > 0:
                results += f"\n{players[player_id]['fname']} - {scores} мячей"
                players[player_id]['scors'] += scores

#        for player_id in game["players"]:
        bot.send_message(chat_id=ch_id,
                         text=results)

        db["game"] = {
                      "players": {},
                      "active": False,
                      "text_list": "Болванка на игру",
                      "list": [],
                      "text": "Болванка на игру",
                      "added": []
                      }
# '''
#                                                            >>>>>>>>>  DELETE
# '''
    elif call.data == "del":
        text = f'*ИГРА ОТМЕНЕНА!!!!\n*{game["text"]}\n\n'
        game['active'] = False
        for player_id in players:

            if player_id in game["players"]:
                bot.edit_message_text(text=text,
                                      chat_id=player_id,
                                      message_id=game["players"][player_id],
                                      parse_mode="Markdown")
            else:
                bot.edit_message_text(text=text,
                                      chat_id=player_id,
                                      message_id=players[player_id]['m_id'],
                                      parse_mode="Markdown")

        db["game"] = {
                  "players": {},
                  "active": False,
                  "text_list": "Болванка на игру",
                  "list": [],
                  "text": "Болванка на игру",
                  "added": []
                  }

    uploadDB(db)


addings = ['edit_game', 'spam', 'add']
@bot.callback_query_handler(func=lambda call: call.data in addings)
def callback_func(call):
    ch_id = str(call.message.chat.id)
    msg_id = str(call.message.message_id)

    if call.data == "spam":
        msg = "Напиши мне что я должен разослать всем:"

    elif call.data == 'edit_game':
        msg = "Текст поста:"

    elif call.data == 'add':
        msg = "Кто еще играет?"

    s = bot.send_message(ch_id, msg)
    bot.register_next_step_handler(s, set_game, call.data, msg_id)


def set_game(m, key, msg_id):
    ch_id = str(m.chat.id)

    db = loadDB()
    game = db['game']
    players = db['players']
# '''
#                                                               >>>>>>>>>  SPAM
# '''
    if key == 'spam':
        for n in players:
            bot.forward_message(chat_id=n,
                                from_chat_id=ch_id,
                                message_id=m.message_id)
# '''
#                                                               >>>>>>>>>  ADD
# '''
    elif key == 'add':
        game['added'].append(m.text)
        game['list'].append(m.text)
#        print ("'add' <<<<<<<<<<<<<<<<<<<<<<<")
        game['text_list'] = form_list(game, players)

        for player_id, msg_id in game["players"].items():

            if player_id in db["admins"]:
                bot.edit_message_text(text=game['text_list'],
                                      chat_id=player_id,
                                      message_id=msg_id,
                                      reply_markup=gen_markup(db,
                                                              'admin_buttons',
                                                              player_id))
            else:
                bot.edit_message_text(text=game['text_list'],
                                      chat_id=player_id,
                                      message_id=msg_id)
# '''
#                                                          >>>>>>>>>  NEW GAME
# '''
    elif key == 'edit_game':

        game = {
              "players": {},
              "active": False,
              "text_list": "Болванка на игру",
              "list": [],
              "text": "Болванка на игру",
              "added": []
              }

        game['text_list'] = game['text'] = m.text

        db['game'] = game

        bot.edit_message_text(text=db['game']['text_list'],
                              chat_id=ch_id,
                              message_id=msg_id,
                              reply_markup=gen_markup(db,
                                                      'admin_buttons',
                                                      ch_id))

    bot.delete_message(ch_id, m.message_id)
    bot.delete_message(ch_id, m.message_id - 1)

    uploadDB(db)


def form_teams():

    db = loadDB()
    players = db['game']['list']
#    print ("form_teams() <<<<<<<<<<<<<<<<<<<<<<<")

    random.shuffle(players)
    members = len(players)

    teamA = teamB = teamC = []

    if members < 13:
        teamA = players[0::2]
        teamB = players[1::2]
        teams = {'\nTeam "RED"': teamA, '\nTeam "BLUE"': teamB}
    elif members >= 13:
        teamA = players[0::3]
        teamB = players[1::3]
        teamC = players[2::3]
        teams = {'\nTeam "RED"': teamA,
                 '\nTeam "BLUE"': teamB,
                 '\n\nTeam "NEUTRAL"': teamC}

    text = db['game']['text']+'\nСоставы на эту игру:\n'

    for t in teams:
        text += t + ':\n'
        i = 0
        for players in teams[t]:
            i += 1
            text += f'{i}) {players}\n'

    uploadDB(db)

    return text


def form_list(game, players):

    players_list = f'{game["text"]}\n\nЗаписались на игру:'
    i = 1
    for index, player in enumerate(game["players"], 1):
        name = players[player]["fname"]
        players_list += f'\n{index}) {name}'
        i = index

    i += 1
    dop = game['added']
    if dop:
        players_list += '\n\n+ мизантропы'
        for index, player in enumerate(dop, i):
            players_list += f'\n{index}) {player}'

    return players_list


@bot.message_handler(commands=['IwantToPlayFootball'])
def command_addplayer(m):
    ch_id = str(m.chat.id)

    db = loadDB()
    players = db['players']

    if ch_id not in players:  # if user hasn't used the "/start" command yet:

        dummyUsr = {
                "fname": None,
                "lname": None,
                "uname": None,
                "admin": False
              }

        if m.chat.first_name is not None:
            dummyUsr['fname'] = m.chat.first_name
        if m.chat.last_name is not None:
            dummyUsr['lname'] = m.chat.last_name
            dummyUsr['fname'] += ' ' + m.chat.last_name
        if m.chat.username is not None:
            dummyUsr['uname'] = m.chat.username

        players[ch_id] = dummyUsr
        uploadDB(db)
        command_start(m)
        bot.send_message(383621032,
                         f'У нас новый игрок -> {dummyUsr["fname"]}')

    else:
        bot.send_message(ch_id, "Хмм...второй раз это ни к чему )")
        command_start(m)


db = loadDB()
db["crashed"] = db["crashed"] + 1
uploadDB(db)

r = bot.send_message("@prj360Test", f'Crashed {db["crashed"]}й раз')
# print (r.message_id)
bot.polling(interval=2, timeout=50)

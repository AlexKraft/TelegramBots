# -*- coding: utf-8 -*-


import telebot, json, random

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


#import logging
#logger = telebot.logger
#telebot.logger.basicConfig(filename='filename.log', level=logging.DEBUG,format=' %(asctime)s - %(levelname)s - %(message)s')


API_TOKEN = '750042395:AAEIWfleAt9JE-JeNIznYEdK70RfasKpXec'


#knownUsers = []  # todo: save these in a file,
#userStep = {}  # so they won't reset every time the bot restarts
#
#commands = {  # command description used in the "help" command
#    'start'       : 'Get used to the bot',
#    'help'        : 'Gives you information about the available commands',
#    'sendLongText': 'A test using the \'send_chat_action\' command',
#    'getImage'    : 'A test using multi-stage messages, custom keyboard, and media sending'
#}

users_dict = {}
game_users = {}
active_push = False
game_text = ''
added_players = []
'''
part where we work with data and sync it with the file on server
'''
def load_db ():
    
    global active_push, users_dict, game_users, game_text
    
    with open('datastore.json', 'r') as f:
        datastore = json.load(f)
    
    users_dict = datastore['users_dict']
    game_users = datastore['game_users']
    active_push = datastore['active_push'] 
    game_text = datastore['game_text']

def upload_db():
    
    with open('datastore.json', 'w') as f:
        datastore = {'users_dict':users_dict,'game_users':game_users,'active_push':active_push,'game_text':game_text}        
        json.dump(datastore, f, indent=2, ensure_ascii=False)     

def add_user_togame():
    
    global game_text, game_users, users_dict
    
    text = game_text + 'Уже записались на игру:\n'
    i = 0
    
    for key in game_users:
        i +=1
        text += f'{i}) {users_dict[str(key)]}\n'
    if len(added_players) != 0:
        for key in added_players:
            i +=1
            text += f'{i}) {key}\n'
        
    return text

def form_teams():
    players = game_users.keys()
    global game_text
    team_list = []
    
    for n in players:
        team_list.append(users_dict[(n)])
    random.shuffle(team_list)
    members = len (team_list)
    
    teamA = teamB = teamC = []
    
    if members < 13:
        teamA = team_list[0::2]
        teamB = team_list[1::2]
        teams = {'Команда A': teamA ,'Команда B': teamB} 
    elif members >= 13:
        teamA = team_list[0::3]
        teamB = team_list[1::3]
        teamC = team_list[2::3]
        teams = {'Команда A': teamA ,'Команда B': teamB,'Команда C': teamC} 
#    else :
#        return 'ДЕЛИТЕСЬ вручную'   
    
    text =  game_text +  'Составы на эту игру:\n'
  
    
    for t in teams:
        text += t + ':\n'
        i = 0
        for players in teams[t]:
            i +=1
            text += f'{i}) {players}\n'
    
    return text



def gen_markup(text, answ):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(text, callback_data=answ))
    return markup


load_db()
bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['start','help'])
def command_start(m):
    cid = m.chat.id
    bot.send_message(cid, "Привет, у тебя должен быть секретный код для того что б пользоваться этим ботом\nПо всем вопросам пиши в группу ФБ https://www.facebook.com/groups/fkalcash/")
    
    
@bot.message_handler(commands=['IwantToPlayFootball'])
def command_addplayer(m):
    cid = m.chat.id
#    print (cid, type(cid))
    if str(cid) not in users_dict:  # if user hasn't used the "/start" command yet:
        
        fname = ''
        lname = '' 
        uname = ''
        global active_push, game_text
        
        if m.chat.first_name is not None:
            fname = m.chat.first_name 
        if m.chat.last_name is not None:
            lname = m.chat.last_name 
        if m.chat.username is not None:
            uname = m.chat.username 
            
        usr = fname + lname + f'(@{uname})'
        users_dict[str(cid)] = usr
        
#        print (users_dict, '\n', type(cid), type(users_dict.keys()))
        
        if active_push:            
            keyboard = gen_markup("+1", "new_player")
            bot.send_message(cid, game_text, reply_markup=keyboard)
        else:
            bot.send_message(cid, "Теперь тебе будут приходить уведомления о играх ;)")
        
        upload_db()
        
    else:
        bot.send_message(cid, "Хмм...второй раз это ни к чему )")


@bot.message_handler(commands=['push'])
def send_query(message):
    cid = message.chat.id
    
    if str(cid) in users_dict:
        global active_push, game_text
        game_text = message.text.replace('/push ','') + '\n'
        keyboard = gen_markup("+1", "new_player")
        
        active_push = True 
        upload_db()
        
        for n in users_dict:
            bot.send_message(n, game_text, reply_markup=keyboard)
    else:
        bot.send_message(cid, "Ты еще не подтвердил секретным кодом что тебе можно")

@bot.message_handler(commands=['gpush'])
def send_alert(m):
    cid = m.chat.id
    
    if str(cid) in users_dict:
        global active_push, game_text
        text = m.text.replace('/gpush ','') + '\n'
            
        for n in users_dict:
            bot.send_message(n, text)
    else:
        bot.send_message(cid, "Ты еще не подтвердил секретным кодом что тебе можно")

@bot.message_handler(commands=['shufle'])
def make_teams(m):
    cid = m.chat.id    
    if str(cid) in users_dict:
        global active_push, game_users
        
        team_text = form_teams()        
        
        for n in game_users:
            bot.edit_message_text(team_text,  chat_id= n,  message_id = game_users[n] )
        
        active_push = False
        game_users = {}
        upload_db()
    else:
        bot.send_message(cid, "Ты еще не подтвердил секретным кодом что тебе можно")
    
    
@bot.message_handler(commands=['edit'])
def edit_push(m):
    cid = m.chat.id    
    if str(cid) in users_dict:
        global game_text
        game_text = m.text.replace('/edit ','') + '\n'
        upload_db()
    else:
        bot.send_message(cid, "Ты еще не подтвердил секретным кодом что тебе можно")

@bot.message_handler(commands=['add'])
def add_player(m):
    cid = m.chat.id    
    global added_players
    if str(cid) in users_dict:
        added_players.append(m.text.replace('/add ',''))
        upload_db()
    else:
        bot.send_message(cid, "Ты еще не подтвердил секретным кодом что тебе можно")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global active_push, game_users 
#    print (f'{game_users}\n{users_dict}\n{active_push}')
    if active_push:
        
        ch_id = call.message.chat.id
        msg_id = call.message.message_id       
        
        if call.data == "new_player":   
            game_users[str(ch_id)] = msg_id
            bot.answer_callback_query(call.id, "До встречи на поле.")
            
            
#            players_list = add_user_togame()
#            
#            for n in game_users:
#                bot.edit_message_text(players_list,  chat_id= n,  message_id = game_users[n] )
#                bot.edit_message_reply_markup(chat_id= n, message_id = game_users[n], reply_markup=keyboard)
        
        elif call.data == "deny":
            game_users.pop(str(ch_id))                     
            bot.answer_callback_query(call.id, "Жаль")            
            sad_text = "Жаль это слышать, но раз так выходит...\nВозможно в следующий раз"
            sad_keyboard = gen_markup("Если все же передумаешь...", "new_player") 
            
            bot.edit_message_text(sad_text,  chat_id = ch_id,  message_id = msg_id )
            bot.edit_message_reply_markup(chat_id = ch_id, message_id = msg_id, reply_markup = sad_keyboard)
            
#            players_list = add_user_togame()
#            
#            for n in game_users:
#                bot.edit_message_text(players_list,  chat_id= n,  message_id = game_users[n] )
#                bot.edit_message_reply_markup(chat_id= n, message_id = game_users[n], reply_markup=keyboard)
        
        keyboard = gen_markup("Передумал", "deny")    
        players_list = add_user_togame()
            
        for n in game_users:
            bot.edit_message_text(players_list,  chat_id= n,  message_id = game_users[n] )
            bot.edit_message_reply_markup(chat_id= n, message_id = game_users[n], reply_markup=keyboard)
            
        upload_db()
        
    else:
        pass
    
    

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    bot.reply_to(message, "я этого не делаю....")





bot.polling(interval=4, timeout=200)
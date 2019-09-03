import telebot, json, random, re

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup ,KeyboardButton, ReplyKeyboardRemove



API_TOKEN = '989604812:AAE1NWU3CwhDfo41ucg80nE2aboimTmlDtQ'#'750042395:AAEIWfleAt9JE-JeNIznYEdK70RfasKpXec'

bot = telebot.TeleBot(API_TOKEN)

data = 'db.json'

def loadDB():
    db = json.load(open(data, "r"))
    return db

def uploadDB(db):
    print("DB UPLOADED!!!!!!!!!!!!!!!!")
    json.dump(db, open(data, "w+"), indent = 2, ensure_ascii=False) 


def gen_markup(db, key = None, ch_id = None):
    
    markup = InlineKeyboardMarkup()   
    
    if key == 'create':
        markup.add(InlineKeyboardButton('Создать игру',callback_data = 'edit_game'))        
        markup.add(InlineKeyboardButton('Рассылка',callback_data = 'spam'))       
        
    elif key == 'post':
        markup.add(InlineKeyboardButton('Постим?',callback_data = 'post'))
           
    elif key == 'show':
        
        if ch_id not in db['game']["players"]:
            markup.add(InlineKeyboardButton('Зарегистрироваться на игру',callback_data = 'reg'))
            
        markup.add(InlineKeyboardButton('Добавить игрока',callback_data = 'add'))
        markup.add(InlineKeyboardButton('Поделить на команды',callback_data = 'shuffle'))
        markup.add(InlineKeyboardButton('Отменить игру',callback_data = 'del'))
        markup.add(InlineKeyboardButton('Рассылка',callback_data = 'spam'))
    
    elif key == 'statistics':
       for k in db['game']["players"]:
            markup.add(InlineKeyboardButton(f"Гол: {db['players'][k]['fname']}", callback_data = k))
        
       markup.add(InlineKeyboardButton('Конец игры',callback_data = 'end'))
       
    elif key == 'new_player':
        markup.add(InlineKeyboardButton('Зарегистрироваться на игру',callback_data = 'reg'))
        
    return markup

    
@bot.message_handler(commands=['start'])
def command_start(m):
    ch_id = str(m.chat.id)
    msg_id = m.message_id
    
    db = loadDB()
    users = db['players']
    
    print("START")
    if ch_id in users:
        print("IN USERS")
        if users[ch_id]["admin"]: 
            print("ADMIN")
            if db['game']['active']:
                print("'game']['active'")
                
                bot.send_message(chat_id = ch_id, 
                                  text = db['game']['text_list'], 
                                  reply_markup = gen_markup(db, 'show',ch_id))
                
#                db["game"]["players"][ch_id] = str (msg_id + 1)
#                uploadDB(db)
            else:
                print("'game']NOT['active'")
                bot.send_message(chat_id = ch_id, 
                                  text = "Че надо?", 
                                  reply_markup = gen_markup(db, 'create'))
        else:
            print("NOT ADMIN")
            if db['game']['active']:
                print("'game']['active'")
#                db["game"]["players"][ch_id] = str (msg_id + 1)
                if ch_id in db['game']['players']:
                    bot.send_message(chat_id = ch_id, 
                                     text = db['game']['text_list'])
                    db["game"]["players"][ch_id] = str (msg_id + 1)
#                    uploadDB(db)
                else:
                    bot.send_message(chat_id = ch_id, 
                                     text = db['game']['text_list'],
                                     reply_markup = gen_markup(db, 'new_player'))
                    
#                    uploadDB(db)
            else:
                print("'game']NOT['active'")
                bot.send_message(chat_id = ch_id, 
                                 text = "Жди уведомление, пока что нет активных игр")
    else:
        bot.send_message(ch_id, "Привет, у тебя должен быть секретный код для того что б пользоваться этим ботом\nПо всем вопросам пиши в группу ФБ https://www.facebook.com/groups/fkalcash/")
        bot.send_message(383621032, f'Кто-то стучится -> {m.chat.first_name} @{m.chat.username}')
        
        
    print (db["game"]["players"])
    uploadDB(db)
    
@bot.callback_query_handler(func=lambda call: re.match('\d{9}', call.data))
def get_game_stat(call):
    who = call.data
    db = loadDB()
    players = db['game']['players']
    
    players[who] += 1
    
    uploadDB(db)
    
    
handle = ['post','reg', 'shuffle', 'del', 'end']   
@bot.callback_query_handler(func=lambda call: call.data in handle)
def callback_func_p(call):      
    ch_id = str(call.message.chat.id)
    msg_id = str(call.message.message_id)
    
    db = loadDB()
    players = db['players'] 
    game = db['game']
    
    if call.data == "post":
#        bot.delete_message(ch_id,msg_id)
        game['active'] = True
        
        for n in players:
            
            if players[n]["admin"]:
                bot.edit_message_reply_markup(chat_id=ch_id, 
                                              message_id=msg_id,
                                              reply_markup=gen_markup(db, 'show', ch_id))
            else:
                bot.send_message(chat_id = n, 
                                 text = game['text_list'],
                                 reply_markup = gen_markup(db, 'new_player'))
                
    elif call.data == "reg":
        game["players"].setdefault(ch_id, msg_id)
        
        game['list'].append(players[ch_id]["fname"])
        print ("'reg' <<<<<<<<<<<<<<<<<<<<<<<")
        game['text_list'] = form_list(game,players) 
        
        for player_id, msg_id in game["players"].items():
            if players[player_id]["admin"]:
                bot.edit_message_text(text = game['text_list'],  
                                      chat_id = player_id, 
                                      message_id = msg_id,
                                      reply_markup = gen_markup(db, 'show',ch_id))
            else:
                bot.edit_message_text(text = game['text_list'],  
                                      chat_id = player_id, 
                                      message_id = msg_id)#,reply_markup = gen_markup(db, 'deny')
        
        db['game'] = game
        
    
    elif call.data == "shuffle":
        game["text_list"] = form_teams()
        game['active'] = False
        for player_id, msg_id in game["players"].items():
            if players[player_id]["admin"]:
                bot.edit_message_text(text = game["text_list"],  
                                      chat_id = player_id, 
                                      message_id = msg_id,
                                      reply_markup = gen_markup(db, 'statistics'))
            else:
                bot.edit_message_text(text = game["text_list"],  
                                      chat_id = player_id, 
                                      message_id = msg_id)
            
            game["players"][player_id] = 0
            
    
    elif call.data == "end":
#        text = form_scores(db)
        results = "В этой игре отметились забив:"
        bot.edit_message_reply_markup(chat_id=ch_id, 
                                      message_id=msg_id)
        
        sorted_x = sorted(game["players"].items(), key = lambda kv: -kv[1])

        for player_id, scores in sorted_x:
            if scores > 0:
                results += f"\n{players[player_id]['fname']} - {scores} мячей"
                players[player_id]['scors'] += scores
        
        for player_id in game["players"]:
            bot.send_message(chat_id = player_id, 
                             text = results)
            
            
    elif call.data == "del":
        text = f'*ИГРА ОТМЕНЕНА!!!!\n*{game["text"]}\n\n'
        game['active'] = False
        for player_id, msg_id in game["players"].items():
            bot.edit_message_text(text = text,  
                                  chat_id = player_id, 
                                  message_id = msg_id, 
                                  parse_mode = "Markdown")
            
#        game = db["dummyGame"]
        
    uploadDB(db)
    print ("END")
    
    
    
addings = ['edit_game','spam','add']
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
    
    print("callback_query_handler<<<<'edit_game','spam','add'<<<<<<<<<<<<<",msg_id)
      
def set_game (m, key,msg_id): 
    
    ch_id = str (m.chat.id)

    
    
#    bot.delete_message(ch_id,msg_id) 
    
    db = loadDB()
    game = db['game']
    players = db['players']

    if key == 'spam':
        
#        bot.delete_message(ch_id,msg_id) 
        
#        text = m.text
        for n in players:
            bot.forward_message(chat_id = n,
                                from_chat_id = ch_id,
                                message_id = m.message_id)
#            bot.send_message(chat_id = n, 
#                             text = text)             
#        command_start(m)
    
    
    
    elif key == 'add':
        game['added'].append(m.text)
        game['list'].append(m.text)
        print ("'add' <<<<<<<<<<<<<<<<<<<<<<<")
        game['text_list'] = form_list(game,players) 
        
        for player_id, msg_id in game["players"].items():
            if players[player_id]["admin"]:
                bot.edit_message_text(text = game['text_list'],  
                                      chat_id = player_id, 
                                      message_id = msg_id,
                                      reply_markup = gen_markup(db, 'show',ch_id))
            else:
                bot.edit_message_text(text = game['text_list'],  
                                      chat_id = player_id, 
                                      message_id = msg_id)      
                
#        bot.delete_message(ch_id,m.message_id)
#        bot.delete_message(ch_id,m.message_id - 1)    
        
    elif key == 'edit_game':
              
        game = {
              "players":{},
              "active": False,
              "text_list":"",
              "list":[],
              "text": "Болванка на игру",
              "added":[]
              }
        
        game['text'] = m.text
        
        game['text_list'] = game['text']
        
        db['game'] = game
        
        bot.edit_message_text(text = game['text_list'],  
                              chat_id = ch_id, 
                              message_id = msg_id,
                              reply_markup = gen_markup(db, 'post'))
        
    bot.delete_message(ch_id,m.message_id)
    bot.delete_message(ch_id,m.message_id - 1)    
     
    uploadDB(db)  


def form_teams():    
    
    db = loadDB()
    players = db['game']['list']
    print ("form_teams() <<<<<<<<<<<<<<<<<<<<<<<")
        
    random.shuffle(players)
    members = len (players)
    
    teamA = teamB = teamC = []
    
    if members < 13:
        teamA = players[0::2]
        teamB = players[1::2]
        teams = {'\nTeam "RED"': teamA ,'\nTeam "BLUE"': teamB} 
    elif members >= 13:
        teamA = players[0::3]
        teamB = players[1::3]
        teamC = players[2::3]
        teams = {'\nTeam "RED"': teamA ,'\nTeam "BLUE"': teamB,'\n\nTeam "NEUTRAL"': teamC} 
#    else :
#        return 'ДЕЛИТЕСЬ вручную'   
    
    text =  db['game']['text'] +  '\nСоставы на эту игру:\n'
  
    
    for t in teams:
        text += t + ':\n'
        i = 0
        for players in teams[t]:
            i +=1
            text += f'{i}) {players}\n'
        
    uploadDB(db)
    
    return text

def form_list(game,players):
    
    players_list = f'{game["text"]}\n\nЗаписались на игру:'
    i = 1
    for index,player in enumerate(game["players"],1):
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

#def form_scores(db):
#    
#    results = "В этой игре отметились:"
#    
#    for player in db['game']['players']:
#        if db['game']['players'][player] > 0 :
#            results += f"\n{db['players'][player]['fname'] - {db['game']['players'][player]} мячей"
#            db['players'][player]['scors'] += db['game']['players'][player]
#            
#    return results

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
        bot.send_message(383621032, f'У нас новый игрок -> {dummyUsr["fname"]}')
        
    else:
        bot.send_message(cid, "Хмм...второй раз это ни к чему )")
        command_start(m)
            

db = loadDB()
db["crashed"] = db["crashed"] + 1
uploadDB(db)

bot.send_message(383621032, f'Crashed {db["crashed"]}й раз')

bot.polling( interval=2, timeout=40)
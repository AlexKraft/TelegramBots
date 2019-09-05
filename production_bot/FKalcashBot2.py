import telebot, json, random, re 
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup ,KeyboardButton, ReplyKeyboardRemove



API_TOKEN = '989604812:AAE1NWU3CwhDfo41ucg80nE2aboimTmlDtQ'#'750042395:AAEIWfleAt9JE-JeNIznYEdK70RfasKpXec'

bot = telebot.TeleBot(API_TOKEN)

data = 'db.json'

'''
     ф-ции загрузки и выгрузки из файла базы данных 
     
     так как обращение в базу происходит в каждой из функций отделно, то
     даже при запущенном боте можно менять файл 'db.json' 
     - добавлять/удалять ["players"]
     - добавлять/удалять ["admins"]
     - вносить изменения в ["game"]
     
'''
def loadDB():
    with open(data, 'r', encoding='utf-8') as f:    
        db = json.load(f)
    return db

def uploadDB(db):
    with open(data, 'w+', encoding='utf-8') as f:
        json.dump(db, f, indent = 2, ensure_ascii=False) 

'''
    маркапы с кнопками:
        
        admin_buttons - если есть запощеная игра то кнопки:
                            add,shuffle,del и spam
                        если нет игры то:
                            edit_game, post и spam
                            
        new_player - кнопки для не админов. если есть игра :  reg      
                                            если нет, то None
        
        statistics - берет участников из db["game"]["players"] и делает кнопку
                    на каждого для фиксации забитых мячей. 
                    эта фунция использует db["game"]["players"] где после shuffle
                    у каждого игрока хранится уже не msg_id, а число забитых мячей.
                    так как после shufle редактирование игрового сообщения не требуется
                    
''' 
def gen_markup(db, key = None, ch_id = None):
    
    markup = InlineKeyboardMarkup()   
   
    if key == 'admin_buttons':
        if not db['game']['active']:
            markup.add(InlineKeyboardButton('Редактировать пост',callback_data = 'edit_game')) 
            markup.add(InlineKeyboardButton('Постим?',callback_data = 'post'))
        else:
            markup.add(InlineKeyboardButton('Добавить игрока',callback_data = 'add'))
            markup.add(InlineKeyboardButton('Поделить на команды',callback_data = 'shuffle'))
            markup.add(InlineKeyboardButton('Отменить игру',callback_data = 'del'))
            
        markup.add(InlineKeyboardButton('Рассылка',callback_data = 'spam'))
      
    elif key == 'new_player':
        
        if not db['game']['active']:
            return None
        elif ch_id not in db["game"]["players"]:
            markup.add(InlineKeyboardButton('Зарегистрироваться на игру',callback_data = 'reg'))
        else:
            return None
        
    elif key == 'statistics':
       for k in db['game']["players"]:
            markup.add(InlineKeyboardButton(f"Гол: {db['players'][k]['fname']}", callback_data = k))
        
       markup.add(InlineKeyboardButton('Конец игры',callback_data = 'end'))
     
    return markup

        

'''
    проверки:
        1) есть ли такой ID в списке общем db['players']
        2) админ или нет в db["admins"]
        3) есть игра или нет по db['game']['active']
    
    админам в ответ отправляет свой набор кнопок в gen_markup
    
Пара важных моментов:
    если админ есть в db["game"]['players'] то обновляется msg_id по которому 
    ему в дальнейшем будут приходить все изменения 
''' 
@bot.message_handler(commands=['start'])
def command_start(m):
    ch_id = str(m.chat.id)
    msg_id = m.message_id
    
    db = loadDB()
    users = db['players']
    
    if ch_id in users:
        
        if ch_id in db["admins"]:
            markup = gen_markup(db, 'admin_buttons',ch_id)
            msg = db['game']['text_list']
            
            if db['game']['active'] and ch_id in db['game']['players']:
                print ("NEW MESSAGE ID <<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                db['game']['players'][ch_id] = msg_id + 1 
        else:
            markup = gen_markup(db, 'new_player')
            msg = db['game']['text_list'] if db['game']['active'] else "пока что нет активных игр"
            
    else:
        msg = "Привет, у тебя должен быть секретный код для того что б пользоваться этим ботом\nПо всем вопросам пиши в группу ФБ https://www.facebook.com/groups/fkalcash/"
        markup = None
        bot.send_message(383621032, f'Кто-то стучится -> {m.chat.first_name} @{m.chat.username}')
        
    bot.send_message (chat_id = ch_id, 
                      text = msg, 
                      reply_markup = markup)

    uploadDB(db)


'''
    сюда мы попадаем после того как поделились на команды и админам вывелись кнопочки 
    с именами игроков по нажатию на которые call.data содержит ID игрока
''' 
@bot.callback_query_handler(func=lambda call: re.match('\d{9}', call.data))
def get_game_stat(call):
    who = call.data
    db = loadDB()
    players = db['game']['players']    
    players[who] += 1    
    uploadDB(db)

'''
    есть два типа хэндлеров. Первые просто в тупую обрабатываю нажатия кнопок,
    вторые будут дальше.
    
    Здесь обрабатывается нажатие на: ['post','reg', 'shuffle', 'del', 'end']
    
    post    - делает рассылку новой игры всем из списка "players"
    reg     - проверяет есть ли игра и если да вносит ID в db["game"]["players"] и сохраняет
            адрес сообщения что б потом его редактировать
    shuffle - вызывает отдельную ф-цию которая берет список и тасует на команды +
            обновляет всем сообщение из db["game"]["players"]
    del     - отмена игры, редактирование сообщения с игрой у всех 
            кто в списке db["game"]["players"], очистка db["game"]
    end     - кнопка 'Конец игры' после того как поделило на команды
            обновляет db["players"] в соответствии с забитыми голами и делает
            те же процедуры что и del
'''    
    
handle = ['post','reg', 'shuffle', 'del', 'end']   
@bot.callback_query_handler(func=lambda call: call.data in handle)
def callback_func_p(call):      
    ch_id = str(call.message.chat.id)
    msg_id = str(call.message.message_id)
    
    db = loadDB()
    players = db['players'] 
    game = db['game']


#                                                                >>>>>>>>>  POST
   
    if call.data == "post":
        game['active'] = True
        bot.delete_message(ch_id,msg_id)
        
        for n in players:            
#            if n in db["admin"]::
#                bot.edit_message_reply_markup(chat_id=ch_id, 
#                                              message_id=msg_id,
#                                              reply_markup=gen_markup(db, 'show', ch_id))
#            else:
            r = bot.send_message(chat_id = n, 
                             text = game['text_list'],
                             reply_markup = gen_markup(db, 'new_player', n))
            players[n]['m_id'] = r.message_id
#'''
##                                                                 >>>>>>>>>  REG
#'''                     
    elif call.data == "reg":
        if game["active"]:
            game["players"].setdefault(ch_id, msg_id)
            
            game['list'].append(players[ch_id]["fname"])
            print ("'reg' <<<<<<<<<<<<<<<<<<<<<<<")
            game['text_list'] = form_list(game,players) 
            
            for player_id, msg_id in game["players"].items():
    #            if players[player_id]["admin"]:
    #                bot.edit_message_text(text = game['text_list'],  
    #                                      chat_id = player_id, 
    #                                      message_id = msg_id,
    #                                      reply_markup = gen_markup(db, 'show',ch_id))
    #            else:
                bot.edit_message_text(text = game['text_list'],  
                                      chat_id = player_id, 
                                      message_id = msg_id)
            
            db['game'] = game
        else:
            bot.delete_message(ch_id,call.message.message_id)
            command_start(call.message)
#'''
#                                                              >>>>>>>>>  SHUFLE
#'''       
    elif call.data == "shuffle":
        game["text_list"] = form_teams()
        game['active'] = False
        
        for player_id in players:
            
            if player_id in game["players"]:
                if player_id in db["admins"]:
                    bot.edit_message_text(text = game["text_list"],  
                                          chat_id = player_id, 
                                          message_id = msg_id,
                                          reply_markup = gen_markup(db, 'statistics'))
                else:
                    bot.edit_message_text(text = game["text_list"],  
                                          chat_id = player_id, 
                                          message_id = msg_id)
                    
            else:
                 bot.edit_message_text(text = '*Вы пропустили эту игру* \n',  
                                          chat_id = player_id, 
                                          message_id = players[player_id]['m_id'], 
                                          parse_mode = "Markdown")
                    
#        for player_id, msg_id in game["players"].items():
#            if ch_id in db["admins"]:
#                bot.edit_message_text(text = game["text_list"],  
#                                      chat_id = player_id, 
#                                      message_id = msg_id,
#                                      reply_markup = gen_markup(db, 'statistics'))
#            else:
#                bot.edit_message_text(text = game["text_list"],  
#                                      chat_id = player_id, 
#                                      message_id = msg_id)
            
            game["players"][player_id] = 0
            
#'''
#                                                                >>>>>>>>>  END
#'''       
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
            
        db["game"] = {
                      "players":{},
                      "active": False,
                      "text_list":"Болванка на игру",
                      "list":[],
                      "text": "Болванка на игру",
                      "added":[]
                      }    
#'''
#                                                               >>>>>>>>>  DELETE
#'''               
    elif call.data == "del":
        text = f'*ИГРА ОТМЕНЕНА!!!!\n*{game["text"]}\n\n'
        game['active'] = False
        for player_id in players:
            
            if player_id in game["players"]:
                bot.edit_message_text(text = text,  
                                      chat_id = player_id, 
                                      message_id = game["players"][player_id], 
                                      parse_mode = "Markdown")
            else:
                bot.edit_message_text(text = text,  
                                      chat_id = player_id, 
                                      message_id = players[player_id]['m_id'], 
                                      parse_mode = "Markdown")
 
        db["game"] = {
                  "players":{},
                  "active": False,
                  "text_list":"Болванка на игру",
                  "list":[],
                  "text": "Болванка на игру",
                  "added":[]
                  }
        
    uploadDB(db)
    
    
'''
    вторые выводят сообщение с текстом. и ставят спец функцию set_game на 
    отработку следующего сообщения. Т.е. следующее сообщение, вне зависимости
    от его содержания будет обработано в функции set_game
    
    
    Здесь обрабатывается нажатие на: ['edit_game','spam','add']
    
    обработчик просит в сообщении скинуть нужный текст у пользователя 
    
    edit_game    - текст для сообщения об игре   
    spam    - любой текст который разошлется всем   
    add     - Имя игрока которого надо записать на игру
    
'''      
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
    
'''
    В ответ на сообщение из предыдущей функции 
    
    spam    - форвардит сообщение от админа всем в db["players"] 
    add     - добавляет имя в db["game"]["added"] и db["game"]["list"],
            редактирует текст со списком игроков db["game"]["text_list"]
            и редактирует сообщение у всех кто подписался на игру db["game"]["players"]
            
    edit_game    - очищает db["game"] и записыват текст пришедший в 
                db["game"]["text"] и ["text_list"]
      
'''     
def set_game (m, key,msg_id): 
    ch_id = str (m.chat.id)
    
    db = loadDB()
    game = db['game']
    players = db['players']
#'''
#                                                                >>>>>>>>>  SPAM
#'''   
    if key == 'spam':
        for n in players:
            bot.forward_message(chat_id = n,
                                from_chat_id = ch_id,
                                message_id = m.message_id)
#'''
#                                                                >>>>>>>>>  ADD
#'''   
    elif key == 'add':
        game['added'].append(m.text)
        game['list'].append(m.text)
        print ("'add' <<<<<<<<<<<<<<<<<<<<<<<")
        game['text_list'] = form_list(game,players) 
        
        for player_id, msg_id in game["players"].items():
            
            if player_id in db["admins"]:
                print ('>>>>>>>Right place')
                bot.edit_message_text(text = game['text_list'],  
                                      chat_id = player_id, 
                                      message_id = msg_id,
                                      reply_markup = gen_markup(db, 'admin_buttons',player_id))
            else:
                bot.edit_message_text(text = game['text_list'],  
                                      chat_id = player_id, 
                                      message_id = msg_id)      
#'''
#                                                            >>>>>>>>>  NEW GAME
#'''       
    elif key == 'edit_game':
              
        game = {
              "players":{},
              "active": False,
              "text_list":"Болванка на игру",
              "list":[],
              "text": "Болванка на игру",
              "added":[]
              }
       
        game['text_list'] = game['text'] = m.text
        
        db['game'] = game
        
        bot.edit_message_text(text = db['game']['text_list'],  
                              chat_id = ch_id, 
                              message_id = msg_id,
                              reply_markup = gen_markup(db, 'admin_buttons',ch_id)) #<<<<<<<<<<<<<<<
        
    bot.delete_message(ch_id,m.message_id)
    bot.delete_message(ch_id,m.message_id - 1)    
     
    uploadDB(db)  

'''
    вспомогательная функция по делению на команды.
    
    просто делает shuffle db['game']['list']
    и оборачивает его в текст
'''
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

    text =  db['game']['text'] +  '\nСоставы на эту игру:\n'
  
    
    for t in teams:
        text += t + ':\n'
        i = 0
        for players in teams[t]:
            i +=1
            text += f'{i}) {players}\n'
        
    uploadDB(db)
    
    return text

'''
     вспомогательная функция для формирования списка игроков из:
           db['game']["players"]
         и db['game']["added"]
         
    результат записывают в виде текста который потом исп для редактирования 
    сообщений у игроков из db['game']["players"]
'''
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


'''
    добавление новых персонажей в db["players"]
    и оповещение меня о новом игроке
'''
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

r = bot.send_message(383621032, f'Crashed {db["crashed"]}й раз')
print (r.message_id)
bot.polling( interval=2, timeout=40)
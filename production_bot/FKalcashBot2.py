import telebot, json, random

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup ,KeyboardButton, ReplyKeyboardRemove



API_TOKEN = '750042395:AAEIWfleAt9JE-JeNIznYEdK70RfasKpXec'

bot = telebot.TeleBot(API_TOKEN)

data = 'datastore.json'

def loadDB():
    db = json.load(open(data, "r"))
    return db

def uploadDB(db):
    json.dump(db, open(data, "w+"), indent = 2, ensure_ascii=False) 


def gen_markup(db, key = None):
    
    markup = InlineKeyboardMarkup()   
    
    if key == 'create':
        markup.add(InlineKeyboardButton('Создать игру',callback_data = 'edit_game'))        
        markup.add(InlineKeyboardButton('Рассылка',callback_data = 'spam'))       
        
    elif key == 'post':
        markup.add(InlineKeyboardButton('Постим?',callback_data = 'post'))
        
    elif key == 'show':
        markup.add(InlineKeyboardButton('Добавить игрока',callback_data = 'add'))
        markup.add(InlineKeyboardButton('Поделить на команды',callback_data = 'shuffle'))
        markup.add(InlineKeyboardButton('Рассылка',callback_data = 'spam'))
    
    elif key == 'new_player':
        markup.add(InlineKeyboardButton('Зарегистрироваться на игру',callback_data = 'reg'))
    
    elif key == 'edit_game':
        markup.add(InlineKeyboardButton('Редактировать текст',callback_data = 'edit_game')) 
        markup.add(InlineKeyboardButton('Добавить участников',callback_data = 'add_players')) 
        
    return markup

    
@bot.message_handler(commands=['start'])
def command_start(m):
    ch_id = str(m.chat.id)
    
    db = loadDB()
    users = db['players']
    
    if ch_id in users:
        if users[ch_id]["admin"]:  
            if db['game']['active']:
                bot.send_message(chat_id = ch_id, 
                                  text = db['game']['text'] + db['game']['text_list'], 
                                  reply_markup = gen_markup(db, 'show'))
            else:
                bot.send_message(chat_id = ch_id, 
                                  text = "Че надо?", 
                                  reply_markup = gen_markup(db, 'create'))
    else:
        bot.send_message(ch_id, "Привет, у тебя должен быть секретный код для того что б пользоваться этим ботом\nПо всем вопросам пиши в группу ФБ https://www.facebook.com/groups/fkalcash/")


handle = ['post','reg', 'shuffle']   
@bot.callback_query_handler(func=lambda call: call.data in handle)
def callback_func_p(call):      
    ch_id = str(call.message.chat.id)
    msg_id = str(call.message.message_id)
    
    db = loadDB()
    players = db['players'] 
    game = db['game']
    
    if call.data == "post":
        game['active'] = True
        for n in players:
            bot.send_message(chat_id = n, 
                             text = game['text'],
                             reply_markup = gen_markup(db, 'new_player'))
            
    elif call.data == "reg":
        game["players"].setdefault(ch_id, msg_id)
        
        players_list = '\nЗаписались на игру:'
        i = 1
        for index,player in enumerate(game["players"],1):
            name = players[player]["fname"]
            players_list += f'\n{index}) {name}'
            i = index
        
        dop = game["players"]['added']
        if dop:
            players_list += '\n+ мизантропы'
            for index, player in enumerate(dop, i):
                players_list += f'\n{index}) {player}'
                
        game['text_list'] = players_list 
        
        for player_id, msg_id in game["players"]:
            
            bot.edit_message_text(text = game['text_list'],  
                                  chat_id = player_id, 
                                  message_id = msg_id)#,reply_markup = gen_markup(db, 'deny')
        
        db['game'] = game["players"]
        db['game'] = game['text_list']
    
    elif call.data == "shuffle":
        
    uploadDB(db)
    
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
    
      
def set_game (m, key,msg_id):  
    ch_id = str (m.chat.id)
    
    
    bot.delete_message(ch_id,m.message_id)
    bot.delete_message(ch_id,m.message_id - 1) 
#    bot.delete_message(ch_id,msg_id) 
    
    db = loadDB()
    players = db['players']
    
    if key == 'spam': 
        text = m.text
        for n in players:
            bot.send_message(chat_id = n, 
                             text = text) 
            
        command_start(m)
        
    elif key == 'add':
        db['game']['added'].append(m.text)
        
        
    elif key == 'edit_game':
        if db['game']['active']:
            game = db["game"]
        else:
            game = db["dummyGame"]
            
        game['text'] = m.text
        db['game'] = game
        
        bot.edit_message_text(text = game['game_text'],  
                              chat_id = ch_id, 
                              message_id = msg_id,
                              reply_markup = gen_markup(db, 'post'))
            
    uploadDB(db)  


def form_teams():
    
    team_list = []
    
    db = loadDB()
    players = db['players']
    dop = db["added"]
    
    for n in players:
        team_list.append(users_dict[(n)])
    if len(added_players) != 0:
        for n in added_players:
            team_list.append(n)
        
    random.shuffle(team_list)
    members = len (team_list)
    
    teamA = teamB = teamC = []
    
    if members < 13:
        teamA = team_list[0::2]
        teamB = team_list[1::2]
        teams = {'\nTeam "RED"': teamA ,'\nTeam "BLUE"': teamB} 
    elif members >= 13:
        teamA = team_list[0::3]
        teamB = team_list[1::3]
        teamC = team_list[2::3]
        teams = {'\nTeam "RED"': teamA ,'\nTeam "BLUE"': teamB,'\n\nTeam "NEUTRAL"': teamC} 
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

    
bot.polling()
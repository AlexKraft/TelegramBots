# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 12:29:20 2019

@author: pc
{
    'dummy': {
        'ch_id'	= trip_id
        'm_id'= ''
        'title'= 'Название поездки'
        'date'= 'Дата: '
        'descr'= 'Описание <- '
        'pic'= None
        'cond'= []
        'price'= []
        'event'= '*ЗАГОЛОВОК*\nДата\nОписание\n\n*Цена:*\n_ЦЕНА1 - условия1_\n_ЦЕНА2 - условия2_'
        'members'= {}
    }
    
}
"""
import telebot
import re

from markups import start_markup, gen_markup, usr_data_markup, remove_markup
from DB_handler import load_dummy, dump_dummy, loadDB, dumpDB, update, newUserDB

API_TOKEN = '989604812:AAE1NWU3CwhDfo41ucg80nE2aboimTmlDtQ'
channel_id = '@prj360Test' #-1001205642456 

main = ["add","trips","back",'post']
addings = ["date","descr","pic","cond","price", 'title']


bot = telebot.TeleBot(API_TOKEN)


def set_usr_data(m, user, call):
    ch_id = str (m.chat.id) 
    
    bot.delete_message(m.chat.id,m.message_id)
    bot.delete_message(m.chat.id,m.message_id - 1)
    
    user['phone'] = m.contact.phone_number
    
    db = loadDB()
    db['users'][ch_id] = user
    newUserDB(db)
    
    reg_forms(call)
    
    
def set_trip (m, key,msg_id):    
    
    print ('>>>>>>>>>>>>>>>>>>>>> KEY ', key)
    
    ch_id = str (m.chat.id) 
    
    dummyDB = load_dummy()
    dummy = dummyDB.setdefault(ch_id, dummyDB['dummy'])
    
    bot.delete_message(m.chat.id,m.message_id)
    bot.delete_message(m.chat.id,m.message_id - 1)
    
    value = m.text
    
    if key == 'price' or key == 'cond':
        dummy[key].append(value)
     
    elif (m.photo):
        pic = m.photo[0].file_id
        dummy[key] = pic 
        
        bot.delete_message(ch_id,msg_id)
        
        bot.send_photo(chat_id = m.chat.id, 
                       photo = pic , 
                       caption = dummy['event'], 
                       reply_markup = gen_markup(dummy, 'new_trip'), 
                       parse_mode = "Markdown")
        
        print ('Got picture <<<<<<<<<<<<<<<<<<<<<<<<<<<<', pic)   
        dummyDB[ch_id] = dummy
        dump_dummy(dummyDB)
        return True
    
    else:
        dummy[key] = value       
        
    dummy['event'] = update(dummy)
    
    if dummy['pic']:
        bot.edit_message_caption(caption = dummy['event'], 
                                 chat_id = ch_id, 
                                 message_id = msg_id, 
                                 reply_markup = gen_markup(dummy, 'new_trip'),   
                                 parse_mode="Markdown")
    else:
        bot.edit_message_text(text = dummy['event'], 
                              chat_id = ch_id, 
                              message_id = msg_id, 
                              reply_markup = gen_markup(dummy, 'new_trip'), 
                              parse_mode= "Markdown")
                           
    dummyDB[ch_id] = dummy
    dump_dummy(dummyDB)
    
    
@bot.message_handler(commands=['start'])
def start_func (m):    
    ch_id = str (m.chat.id) 
    db = loadDB()
    users = db["users"]
    
    if users.setdefault(ch_id, None):        
        if users[ch_id]['admin']:      
            bot.send_message(chat_id = ch_id, 
                             text = "ADMIN buttons", 
                             reply_markup = start_markup(ch_id))  
        else:
            bot.send_message(chat_id = ch_id, 
                          text = 'Актуальные поездки: \n', 
                          reply_markup = gen_markup(db, 'trips_list'), 
                          parse_mode = "Markdown")
        
    else:
        dummyDB = load_dummy()
        newUsr = dummyDB["dummyUsr"]
        
        if m.chat.first_name is not None:
            fname = m.chat.first_name 
            newUsr["fname"]= fname
        if m.chat.last_name is not None:
            lname = m.chat.last_name 
            newUsr["lname"]= lname
        if m.chat.username is not None:
            uname = m.chat.username
            newUsr["uname"]= uname    
        
        db["users"][ch_id] = newUsr
        
        newUserDB(db)        
        
        bot.send_message(chat_id = ch_id, 
                          text = 'Актуальные поездки: \n', 
                          reply_markup = gen_markup(db, 'trips_list'), 
                          parse_mode = "Markdown")
                          
          

@bot.callback_query_handler(func=lambda call: call.data in main)
def callback_func(call): 
    
    ch_id = str(call.message.chat.id)
    msg_id = str(call.message.message_id)
    
    db = loadDB()
    dummyDB = load_dummy()
    dummy = dummyDB.setdefault(ch_id, dummyDB['dummy']) 
    
    

    if call.data == "add":  
        dummy = dummyDB['dummy']
        dummy['event'] = update(dummy)
        text = dummy['event']        
        bot.edit_message_text(text = text, 
                              chat_id = ch_id, 
                              message_id = msg_id,  
                              reply_markup = gen_markup(dummy, 'new_trip'), 
                              parse_mode="Markdown")
        dummyDB[ch_id] = dummy
        dump_dummy(dummyDB)
        
    if call.data == "trips":
        text = 'Актуальные поездки: \n'
        bot.edit_message_text(text = text, 
                              chat_id = ch_id, 
                              message_id = msg_id,  
                              reply_markup = gen_markup(db, 'trips_list'), 
                              parse_mode = "Markdown")
        
    if call.data == "back": 
        
        bot.delete_message(ch_id,msg_id)
        
        if db['users'][ch_id]['admin']:          
            bot.send_message(chat_id = ch_id, 
                             text = "ADMIN buttons", 
                             reply_markup = start_markup(ch_id))          
        else:
            bot.send_message(chat_id = ch_id, 
                              text = 'Актуальные поездки: \n', 
                              reply_markup = gen_markup(db, 'trips_list'), 
                              parse_mode = "Markdown")
            
    if call.data == "post":     
        
        bot.answer_callback_query(call.id, f"Успешно отправленна в канал {channel_id}")
        
        bot.delete_message(ch_id,msg_id)
        
        bot.send_message(ch_id,
                         "ADMIN buttons", 
                         reply_markup = start_markup(ch_id))  
        
        if dummy['pic']:
            bot.send_photo(chat_id = channel_id, 
                           photo = dummy['pic'] , 
                           caption = dummy['event'], 
                           parse_mode = "Markdown")
        
        else:
            bot.send_message(chat_id = channel_id, 
                             text = dummy['event'], 
                             parse_mode = "Markdown")
        
        dumpDB(dummy)
        dummyDB.pop(ch_id)
        dump_dummy(dummyDB)
         
        
@bot.callback_query_handler(func=lambda call: call.data in addings)  
def callback_add_func(call):     
    ch_id = str(call.message.chat.id)
    msg_id = str(call.message.message_id)
    
    if call.data == "date":           
        msg = "New data:"
    
    if call.data == "descr":             
        msg = "New description:"
    
    if call.data == "pic":               
        msg = "New picture:"
        
    if call.data == "cond":                
        msg = "Условия поездки:"
        
    if call.data == "price":     
        msg = "Цена поездки:"     
    
    if call.data == "title":     
        msg = "Новый заголовок:"
        
    s = bot.send_message(ch_id, msg)
    bot.register_next_step_handler(s, set_trip, call.data, msg_id)
  
    
# call for trip_ID
@bot.callback_query_handler(func=lambda call: re.match('\d{14}', call.data))
def get_trip_data(call):
    print("GOT IN HERE get_trip_data")
    ch_id = str(call.message.chat.id)
    msg_id = call.message.message_id
    trip_id = call.data
#    bot.delete_message(ch_id,msg_id)
    
    db = loadDB()
    trips = db['trips']       
    users = db['users']
    
    if trip_id in trips:
        trip = trips[trip_id]
        
        if users[ch_id]['admin']:
#            members_price = trip["members"].keys()
            
            msg ='Зарегистрировано:\n'
            
            for cat in trip["members"]:
                members = trip["members"][cat]
                print (members)
                msg += f'\nНа {cat}:\n'
                i = 1
                for n in members:
                    msg += f'{i}){users[n]["fname"]} {users[n]["lname"]} (@{users[n]["uname"]}): +{users[n]["phone"]}\n'
                    i += 1
            
            bot.edit_message_text(text = msg, 
                                   chat_id = ch_id, 
                                   message_id = msg_id, 
                                   reply_markup = gen_markup(trip))
#       
##            
###        if ch_id in db['admins']:
#        print ("IM IN HERE <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
#        msg ='Зарегистрировано:\n'
#        
#        usrs_price = users.keys()
#        
#        for price in usrs_price:
#            usr = trip['members'][cat]
#            for user in users:
#                pass            
#           
#            members = trip['members']
#            print (members)
#            for price_member in members: 
#                print (price_member)
#                i = 1
#                msg += f'{price_member}:\n'
#                for n in price_member:
#                #                    msg += f'{i}){price_member[n]["fname"]} {price_member[n]["lname"]} (@{price_member[n]["uname"]}): {price_member[n]["phone"]}\n'
#                    print (f'{i}) {n}')
#                    i += i
            
            
            
        else:        
            if trip['pic']:
                bot.delete_message(ch_id,msg_id)
                bot.send_photo(chat_id = ch_id, 
                               photo = trip['pic'] , 
                               caption = trip['event'], 
                               reply_markup = gen_markup(trip, 'register'), 
                               parse_mode = "Markdown")
            else:                
                bot.edit_message_text(text = trip['event'], 
                                      chat_id = ch_id, 
                                      message_id = msg_id, 
                                      reply_markup = gen_markup(trip, 'register'), 
                                      parse_mode = "Markdown")    
            
            dummyDB = load_dummy()  
            dummy = users[ch_id].copy()
            dummy['interested'] = trip_id
            dummyDB[ch_id] = dummy
            dump_dummy(dummyDB)



@bot.callback_query_handler(func=lambda call:  re.match('\d{4}|\d{3}', call.data))
def reg_forms(call):
    
    print ("IM IN HERE REG FORMS<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    ch_id = str(call.message.chat.id)
    msg_id = call.message.message_id
    
    dummyDB = load_dummy()  
    dummy = dummyDB[ch_id]
    trip_id = dummy["interested"]
    
    db = loadDB()
    user = db['users'][ch_id]
    
    if ch_id in db["trips"][trip_id]["members"][call.data]:
        bot.answer_callback_query(call.id, 
                                  text = 'Вы УЖЕ зарегистрированы на поездку',
                                  cache_time = 2)
        
    else:
        if user['phone'] and (user['fname'] or user['lname']):
            bot.answer_callback_query(call.id, 
                                      text = 'вы успешно зарегистрировались',
                                      cache_time = 2)
            
            db['trips'][trip_id]["members"][call.data].append(ch_id)
            newUserDB(db)
            bot.delete_message(ch_id,msg_id)
#            start_func (call.message)
            text = f'Вы успешно зарегистрировались\n{db["trips"][trip_id]["date"]}\n*{db["trips"][trip_id]["title"]}*\nЧекайте на Инфо-лист з умовами туру'
            bot.send_message(chat_id = ch_id, 
                             text = text, 
                             parse_mode = "Markdown", 
                             reply_markup = remove_markup()) 
        else:
            s = bot.send_message(chat_id = ch_id, 
                         text = 'Можно ваш номер?', 
                         parse_mode = "Markdown", 
                         reply_markup = usr_data_markup())    
       
        
            bot.register_next_step_handler(s, set_usr_data, user, call)


#@bot.message_handler(content_types=['contact'])
#def get_contact(m):
#    ch_id = str (m.chat.id)   
#    msg_id = str (m.message_id)
#    
#    usr = m.contact
#    
#    print (usr, usr.phone_number) 
    

    
@bot.message_handler(commands=['test'])
def st_func (m):  
    ch_id = str (m.chat.id)   
    msg_id = str (m.message_id)
#    db = {'dummy': {'ch_id': '',
#          'm_id': '',
#          'title': 'Название поездки',
#          'date': 'Дата: ',
#          'descr': 'Описание <- ',
#          'pic': None,
#          'cond': [],
#          'price': [],
#          'event': '*REAL EVENT*',
#          'members': {}}}
#    dump_dummy(db)
    
    trip = {}
    
    s = bot.send_message(chat_id = ch_id, 
                     text = 'Можно ваш номер?', 
                     parse_mode = "Markdown", 
                     reply_markup = remove_markup())    
   
    
    bot.register_next_step_handler(s, usr_data)
    
    
    
    
  
#    db = loadDB()
#    usr = db["members"]
#        
#    if usr.setdefault(ch_id, None):
#        print ('WE HAVE YOU <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
#    else:
#        newUsr = {}
#        if m.chat.first_name is not None:
#            fname = m.chat.first_name 
#        if m.chat.last_name is not None:
#            lname = m.chat.last_name 
#        if m.chat.username is not None:
#            uname = m.chat.username
#    
#        newUsr["fname"]= fname
#        newUsr["lname"]= lname
#        newUsr["uname"]= uname
#        newUsr["phone"]= None
#        newUsr["admin"]= True
#        
#        db["members"][ch_id] = newUsr
#        
#        newUserDB(db)
#    pass
        
@bot.message_handler(func=lambda message: True)
def message_handler(message):
    print(message.text)
    bot.reply_to(message, "still working")
        
@bot.message_handler(content_types=['location'])
def location(m):
    print (f'LONG:{m.location.longitude} LAT:{m.location.latitude}')
    
@bot.edited_message_handler(content_types=['location'])
def location_edit(m):
    print (f'Location_edited\nLONG:{m.location.longitude} LAT:{m.location.latitude}')
    
bot.polling(interval=2, timeout=100)
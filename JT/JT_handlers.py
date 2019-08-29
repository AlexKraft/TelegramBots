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

from markups import start_markup, gen_markup
from DB_handler import load_dummy, dump_dummy, loadDB, dumpDB, update, newUserDB

API_TOKEN = '989604812:AAE1NWU3CwhDfo41ucg80nE2aboimTmlDtQ'
channel_id = '@prj360Test' #-1001205642456 

main = ["add","trips","back",'post']
addings = ["date","descr","pic","cond","price", 'title']


bot = telebot.TeleBot(API_TOKEN)

def set_pic (m,key,msg_id):    
    print ('FOTO <<<<<<<<<<<<<<<<<<<<<<<<<<<< ', key)    
    ch_id = str (m.chat.id) 
    
    dummyDB = load_dummy()
    dummy = dummyDB.setdefault(ch_id, dummyDB['dummy'])
    
    
    bot.delete_message(m.chat.id,m.message_id)
    bot.delete_message(m.chat.id,m.message_id - 1)
    
    if (m.photo):
        pic = m.photo[0].file_id
        trip['pic'] = pic 
        bot.delete_message(trip['ch_id'],trip['m_id'])
        bot.send_photo(chat_id = m.chat.id, photo = pic , caption = update(trip), reply_markup = new_trip_markup(), parse_mode = "Markdown")
        print ('Got picture <<<<<<<<<<<<<<<<<<<<<<<<<<<<', pic)
    
    else:    
        if trip['pic']:
            bot.edit_message_caption(caption = update(trip), chat_id = trip['ch_id'], message_id = trip['m_id'],   parse_mode="Markdown", reply_markup=new_trip_markup())
        else:
    #        print ('>>>> edit mesage',)
            bot.edit_message_text(text = update(trip), chat_id = trip['ch_id'], message_id = trip['m_id'] ,  reply_markup = new_trip_markup(), parse_mode= "Markdown")
                           
    trip_dict[m.chat.id] = trip    


def set_trip (m,key,msg_id):    
    
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
    users = db["members"]
    
    if users.setdefault(ch_id, None):        
        if users[ch_id]['admin']:      
            bot.send_message(ch_id, "ADMIN buttons", reply_markup = start_markup(ch_id))  
            
    else:
        newUsr = {}
        if m.chat.first_name is not None:
            fname = m.chat.first_name 
        if m.chat.last_name is not None:
            lname = m.chat.last_name 
        if m.chat.username is not None:
            uname = m.chat.username
    
        newUsr["fname"]= fname
        newUsr["lname"]= lname
        newUsr["uname"]= uname
        newUsr["phone"]= None
        newUsr["admin"]= False
        
        db["members"][ch_id] = newUsr
        
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
        dummy['event'] = update(dummy)
        text = dummy['event']        
        bot.edit_message_text(text = text, 
                              chat_id = ch_id, 
                              message_id = msg_id,  
                              reply_markup = gen_markup(dummy, 'new_trip'), 
                              parse_mode="Markdown")
        
    if call.data == "trips":
        text = 'Актуальные поездки: \n'
#        for trip in db['trips']:
#            trip['members'].values()
        bot.edit_message_text(text = text, 
                              chat_id = ch_id, 
                              message_id = msg_id,  
                              reply_markup = gen_markup(db, 'trips_list'), 
                              parse_mode = "Markdown")
        
    if call.data == "back": 
        if db['members'][ch_id]['admin']:          
            bot.edit_message_text(text = "ADMIN buttons", 
                                  chat_id = ch_id, 
                                  message_id = msg_id, 
                                  reply_markup = start_markup(ch_id))        
        else:
            bot.edit_message_text(text = 'Актуальные поездки: \n', 
                                  chat_id = ch_id, 
                                  message_id = msg_id, 
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
    

@bot.callback_query_handler(func=lambda call: re.match('\d{14}', call.data))
def get_trip_data(call):
    print("GOT IN HERE get_trip_data")
    ch_id = str(call.message.chat.id)
    msg_id = call.message.message_id
    trip_id = call.data
#    bot.delete_message(ch_id,msg_id)
    
    db = loadDB()
    trips = db['trips']       
   
    if trip_id in trips:
        trip = trips[trip_id]
        users = db["members"]        
        
       
        if users[ch_id]['admin']:    
#        if ch_id in db['admins']:
            print ("IM IN HERE <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
            msg ='Зарегистрировано:\n'
            
            mem_cat = trip['members'].keys()
            
            for cat in mem_cat:
                usrs = trip['members'][cat]
                for user in users:
                    
            
            members = trip['members']
            print (members)
            for price_member in members: 
                print (price_member)
                i = 1
                msg += f'{price_member}:\n'
                for n in price_member:
#                    msg += f'{i}){price_member[n]["fname"]} {price_member[n]["lname"]} (@{price_member[n]["uname"]}): {price_member[n]["phone"]}\n'
                    print (f'{i}) {n}')
                    i += i
            
            
#            bot.edit_message_text(text = msg, 
#                                   chat_id = ch_id, 
#                                   message_id = msg_id, 
#                                   reply_markup = gen_markup(trip)
#                                  )
        else:        
            if trip['pic']:
                bot.edit_message_caption(caption = trip['event'], 
                                         chat_id = ch_id, 
                                         message_id = msg_id, 
                                         reply_markup = gen_markup(trip, 'register'),   
                                         parse_mode="Markdown")
            else:
                bot.edit_message_text(text = trip['event'], 
                                      chat_id = ch_id, 
                                      message_id = msg_id, 
                                      reply_markup = gen_markup(trip, 'register'), 
                                      parse_mode= "Markdown")    
            
            dummyDB = load_dummy()  
            dummy = users[ch_id].copy()
            dummy['registered'] = {trip_id:None}
            dummyDB[ch_id] = dummy
            dump_dummy(dummyDB)



@bot.callback_query_handler(func=lambda call: re.match('reg', call.data))
def reg_forms(call):
    ch_id = str(call.message.chat.id)
    s = call.data[3:]
    
    dummyDB = load_dummy()  
    dummy = dummyDB[ch_id]
    key = dummy['registered'].keys()
    
#    if re.match('\d{3,4}', s):
#        dummy['registered'][key[-1]] = s
#    
#    if 
    
    
    
                
@bot.message_handler(commands=['test'])
def st_func (m):        
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
#    
    ch_id = str (m.chat.id) 
    db = loadDB()
    usr = db["members"]
        
    if usr.setdefault(ch_id, None):
        print ('WE HAVE YOU <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
    else:
        newUsr = {}
        if m.chat.first_name is not None:
            fname = m.chat.first_name 
        if m.chat.last_name is not None:
            lname = m.chat.last_name 
        if m.chat.username is not None:
            uname = m.chat.username
    
        newUsr["fname"]= fname
        newUsr["lname"]= lname
        newUsr["uname"]= uname
        newUsr["phone"]= None
        newUsr["admin"]= True
        
        db["members"][ch_id] = newUsr
        
        newUserDB(db)
#    pass
        
@bot.message_handler(func=lambda message: True)
def message_handler(message):
    bot.reply_to(message, "still working")
        
    
bot.polling(interval=2, timeout=100)
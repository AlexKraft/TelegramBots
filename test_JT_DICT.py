# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 15:08:55 2019

@author: pc
"""
import telebot, json, re

from datetime import datetime, time

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '989604812:AAE1NWU3CwhDfo41ucg80nE2aboimTmlDtQ'

channel_id = '@prj360Test' #-1001205642456 

bot = telebot.TeleBot(API_TOKEN)

admins = {'383621032': "alex_under_kraft"}

trip_dict = {}

'''

    Inline keyboards markups
    
'''        
def start_markup(ch_id):
    
    markup = InlineKeyboardMarkup()
    
    markup.add(InlineKeyboardButton('Создать поездку',callback_data = 'add'))
    markup.add(InlineKeyboardButton('Поездки',callback_data = 'trips'))
    
    bot.send_message(ch_id, "ADMIN buttons", reply_markup = markup)
    
#    return markup


def new_trip_markup():
    
    markup = InlineKeyboardMarkup()
    
    markup.add(InlineKeyboardButton('Заголовок',callback_data = 'title'),
               InlineKeyboardButton('Дата',callback_data = 'date'),
               InlineKeyboardButton('Описание',callback_data = 'descr'),
               InlineKeyboardButton('Фото',callback_data = 'pic'),
               InlineKeyboardButton('Условия',callback_data = 'cond'),
               InlineKeyboardButton('Цена',callback_data = 'price'))
   
    markup.add(InlineKeyboardButton('Постим?',callback_data = 'post'))
    markup.add(InlineKeyboardButton('Назад', callback_data = 'restart'))
    
    return markup

def get_trips_markup(trips, key = None):
    markup = InlineKeyboardMarkup()
    
    if key == 'title':
        print ('ENTERED')
        for k in trips:
            print ('get_trips_markup<<<<<<<title<<<<<<<<<<',trips[k]['id'])
            markup.add(InlineKeyboardButton(trips[k]['title'], callback_data = trips[k]['id'])) #str(trips[k]['id'])
    
    elif key == 'reg':
        print ('get_trips_markup<<<<<<<reg<<<<<<<<<<',trips.keys())
        for k in trips['price']:
            markup.add(InlineKeyboardButton(f'Register for: {k}', callback_data = k))
            print (k, type(k))
        markup.add(InlineKeyboardButton('Назад', callback_data = 'restart'))
        
    else:
        print ('get_trips_markup<<<<<<<else<<<<<<<<<<')
        for k in trips:
            markup.add(InlineKeyboardButton(trips[k], callback_data = trips[k]))
        
    return markup

'''

    My TRIP dict like object
    
'''
def upload (d):
    
    trip = d
    
    trip['id'] =        datetime.today().strftime("%Y%m%d%H%M%S")
    trip['active'] =    True
    
    
    trips = json.load(open('trips.json', "r"))
    s = trip['title']
    trips[s] = trip        
    json.dump( trips , open('trips.json', "w+"), indent = 2, ensure_ascii=False)
    

   
def init_trip(trip_id):
    trip = {}
    trip['ch_id'] 		= trip_id
    trip['m_id']		= ''
    trip['title'] 		= 'Название поездки'
    trip['date'] 		= 'Дата: '
    trip['descr'] 		= 'Описание <- '
    trip['pic'] 		= None
    trip['cond'] 		= []
    trip['price'] 		= []
    trip['event'] 		= f'*ЗАГОЛОВОК*\nДата\nОписание\n\n*Цена:*\n_ЦЕНА1 - условия1_\n_ЦЕНА2 - условия2_'
    trip['members']		= {}
    
    return trip
 

def update (trip):
    
    tail = '\nЗаписывайтесь у нашего бота -> @prjTestBot\nИли по телефону ..................'
    
    
    if len(trip['price']) == len(trip['cond']):
        price = ''
        for elem in range(len(trip['price'])):
            
            num,des = ''.join(trip['price'][elem]),''.join(trip['cond'][elem])
            price += f'_{num}_ - {des}\n'
            
        trip['event'] = f"*{trip['title']}*\n\nДата: {trip['date']}\n\n{trip['descr']}\n\n*Цена:*\n{price}{tail}"
    else:
        price  = '\n'.join(trip['price'])
        cond  = '\n'.join(trip['cond'])
        trip['event'] = f"*{trip['title']}*\n\nДата: {trip['date']}\n\n{trip['descr']}\n{cond}\n\n*Цена:*\n_{price}_{tail}"
   
    return trip['event']
    

def get_list():
    trips = json.load(open('trips.json', "r"))
    return trips

        
'''

    Keep it clean and update the trip Funcs
    
''' 
def set_pic (m,key):    
    
    print ('FOTO <<<<<<<<<<<<<<<<<<<<<<<<<<<< ', key)
    trip = trip_dict[m.chat.id]
#    print (trip)
    bot.delete_message(m.chat.id,m.message_id)
    bot.delete_message(m.chat.id,m.message_id - 1)
    print ('Deleted <<<<<<<<<<<<<<<<<<<<<<<<<<<<')
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

def set_trip (m,key):    
    
    print ('>>>>>>>>>>>>>>>>>>>>> KEY ', key)
    trip = trip_dict[m.chat.id]
#    print (trip)
    bot.delete_message(m.chat.id,m.message_id)
    bot.delete_message(m.chat.id,m.message_id - 1)
    

    value = m.text
    
#        print (key == 'price' or key == 'cond')
    
    if key == 'price' or key == 'cond':
        trip[key].append(value)
        print ('>>>>>>>> new append value', key, value) 
    else:
        trip[key] = value        
        print ('>>>>>>>> new value', key, value,'\n',trip)  
        
#    bot.delete_message(trip['ch_id'],trip['m_id'])
    
    if trip['pic']:
        bot.edit_message_caption(caption = update(trip), chat_id = trip['ch_id'], message_id = trip['m_id'],   parse_mode="Markdown", reply_markup=new_trip_markup())
    else:
#        print ('>>>> edit mesage',)
        bot.edit_message_text(text = update(trip), chat_id = trip['ch_id'], message_id = trip['m_id'] ,  reply_markup = new_trip_markup(), parse_mode= "Markdown")
                           
    trip_dict[m.chat.id] = trip
    

'''
    Handlers
''' 
@bot.message_handler(commands=['start'])
def start_func (m):    
    ch_id = str (m.chat.id)    
    if ch_id in admins:          
        start_markup(ch_id)        
    else:
        pass

@bot.callback_query_handler(func=lambda call: call.data == "trips")
def get_trips(call):
    trips = get_list()
    
    ch_id = call.message.chat.id
    msg_id = call.message.message_id
    
    bot.delete_message(ch_id,msg_id)
     
    bot.send_message(ch_id, 'Актуальные поездки: ', reply_markup = get_trips_markup(trips, 'title'), parse_mode="Markdown")
 
@bot.callback_query_handler(func=lambda call: re.match('\d{14}', call.data))
def get_trip_data(call):
    print("GOT IN HERE get_trip_data")
    ch_id = call.message.chat.id
    msg_id = call.message.message_id
    
    bot.delete_message(ch_id,msg_id)
    
    trips = get_list()
    for n in trips:
        if call.data in trips[n]['id']:
            trip = trips[n]
            trip_dict[ch_id] = trip
            
            msg = trip['event']#f'{trip["title"]}\nДата:{trip["date"]}\n{trip["cond"]}\n{trip["price"]}'
            if trip["pic"]:
                bot.send_photo(ch_id, trip["pic"] , caption = msg, reply_markup = get_trips_markup(trip, 'reg'), parse_mode="Markdown")  
            else:
                bot.send_message(ch_id, msg, reply_markup = get_trips_markup(trip, 'reg'), parse_mode="Markdown") 
                 
@bot.callback_query_handler(func=lambda call: True)
def callback_set_func(call):    
    
    ch_id = call.message.chat.id
    msg_id = call.message.message_id
    
    
#    trip_dict = get_list()
    
    if call.data == "add":   
        trip = init_trip(ch_id) 
        trip_dict[ch_id] = trip
        bot.send_message(ch_id, trip['event'], reply_markup = new_trip_markup(), parse_mode="Markdown")  
        bot.delete_message(ch_id,msg_id)
    
    if call.data == "title":                       
        msg = "Enter new title:"
        s = bot.send_message(ch_id, msg)
        bot.register_next_step_handler(s, set_trip, call.data)
    
    if call.data == "restart":     
        start_markup(ch_id)
             
    if call.data == "date":           
        msg = "New data:"
        s = bot.send_message(ch_id, msg)
        bot.register_next_step_handler(s, set_trip, call.data)
    
    if call.data == "descr":             
        msg = "New description:"
        s = bot.send_message(ch_id, msg)
        bot.register_next_step_handler(s, set_trip, call.data)
    
    if call.data == "pic":               
        msg = "New picture:"
        s = bot.send_message(ch_id, msg)
        bot.register_next_step_handler(s, set_pic, call.data)
        
    if call.data == "cond":                
        msg = "Условия поездки:"
        s = bot.send_message(ch_id, msg)
        bot.register_next_step_handler(s, set_trip, call.data)
        
    if call.data == "price":     
        msg = "Цена поездки:" 
        s = bot.send_message(ch_id, msg)
        bot.register_next_step_handler(s, set_trip, call.data)
    
    trip_dict[ch_id]['m_id'] = msg_id ### чет надо делать
    
    if call.data == "post":     
        
        trip = trip_dict[ch_id]
        bot.delete_message(ch_id,msg_id) 
        
        if trip['pic']:
            bot.send_photo(chat_id = channel_id, photo = trip['pic'] , caption = update(trip), parse_mode="Markdown")
        
        else:
            bot.send_message(chat_id = channel_id, text = update(trip), parse_mode="Markdown")
        
        upload(trip)
        
        start_markup(ch_id)     
    
    
    
#--------------------------------------------------------------------------------------  

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    bot.reply_to(message, "still working")
    
        
bot.polling()
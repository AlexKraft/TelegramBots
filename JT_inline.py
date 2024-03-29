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

class Trip:
    def __init__(self,trip_id):
        self.trip = {}
        
        
        self.ch_id = trip_id
        self.m_id = ''
        self.title = 'Название поездки'
        self.date = 'Дата: '
        self.descr = 'Описание <- '
        self.pic = None
        self.cond = []
        self.price = []
        self.event = f'*ЗАГОЛОВОК*\nДата\nОписание\n\n*Цена:*\n_ЦЕНА1 - условия1_\n_ЦЕНА2 - условия2_'
        self.members = {}
       
    def __str__ (self):
        print (self.title, self.dates , self.price )

    def update (self):
        
        tail = '\nЗаписывайтесь у нашего бота -> @prjTestBot\nИли по телефону ..................'
        
        print ('---------------> GOT HERE !!!!!!!!!!!!!!!!!', len(self.price) ,len(self.cond), len(self.price) == len(self.cond))
        
        if len(self.price) == len(self.cond):
            price = ''
            for elem in range(len(self.price)):
                num,des = ''.join(self.price[elem]),''.join(self.cond[elem])
                price += f'_{num}_ - {des}\n'
                
            self.event = f'*{self.title}*\n{self.date}\n{self.descr}\n\n*Цена:*\n{price}{tail}'
        else:
            price  = '\n'.join(self.price)
            cond  = '\n'.join(self.cond)
            self.event = f'*{self.title}*\n{self.date}\n{self.descr}\n{cond}\n\n*Цена:*\n_{price}_{tail}'
       
        return self.event
        
    def upload (self):
        trip = {}
        trip['id'] = datetime.today().strftime("%Y%m%d%H%M%S")
        trip['title'] = self.title
        trip['date'] = self.date
        trip['descr'] = self.descr
        trip['cond'] = self.cond
        trip['pic'] = self.pic
        trip['price'] = self.price
        trip['members'] = {}
        trip['active'] = True
    
        trips = json.load(open('trips.json', "r"))
        s = self.title
        trips[s] = trip        
        json.dump( trips , open('trips.json', "w+"), indent=2, ensure_ascii = False)
        
    def get_list():
        trips = json.load(open('trips.json', "r"))
#        print (type(trips), '\n',trips)
        return trips
        
'''
    Keep it clean and update the trip Funcs
''' 
def set_title (m):
    trip = trip_dict[m.chat.id]
    title = m.text
    trip.title = title
    bot.delete_message(m.chat.id,m.message_id)
    bot.delete_message(m.chat.id,m.message_id - 1)  
#    print ('deleted')     
    if trip.pic:
        bot.edit_message_caption(caption= trip.update(), chat_id = trip.ch_id , message_id = trip.m_id, parse_mode="Markdown", reply_markup=new_trip_markup())
    else:
        bot.edit_message_text( trip.update(), chat_id = trip.ch_id , message_id = trip.m_id, reply_markup = new_trip_markup(), parse_mode= "Markdown")
    

def set_date (m):
    date = m.text
    trip = trip_dict[m.chat.id]
    trip.date += date +'\n'
    bot.delete_message(m.chat.id,m.message_id) 
    bot.delete_message(m.chat.id,m.message_id - 1)    
#    bot.send_message(m.chat.id, trip.update(), reply_markup = new_trip_markup())
    if trip.pic:
        bot.edit_message_caption(caption= trip.update(), chat_id = trip.ch_id , message_id = trip.m_id, parse_mode="Markdown", reply_markup=new_trip_markup())
    else:
        bot.edit_message_text( trip.update(), chat_id = trip.ch_id , message_id = trip.m_id, reply_markup = new_trip_markup(), parse_mode= "Markdown")
    

def set_descr (m):
    descr = m.text
    trip = trip_dict[m.chat.id]
    trip.descr = descr
    bot.delete_message(m.chat.id,m.message_id)
    bot.delete_message(m.chat.id,m.message_id - 1)     
    if trip.pic:
        bot.edit_message_caption(caption= trip.update(), chat_id = trip.ch_id , message_id = trip.m_id, parse_mode="Markdown", reply_markup=new_trip_markup())
    else:
        bot.edit_message_text( trip.update(), chat_id = trip.ch_id , message_id = trip.m_id, reply_markup = new_trip_markup(), parse_mode= "Markdown")
    
def set_cond (m):
    cond = m.text
    trip = trip_dict[m.chat.id]
    trip.cond.append(cond)
    bot.delete_message(m.chat.id,m.message_id) 
    bot.delete_message(m.chat.id,m.message_id - 1)  
    
    if trip.pic:
        bot.edit_message_caption(caption= trip.update(), chat_id = trip.ch_id , message_id = trip.m_id, parse_mode="Markdown", reply_markup=new_trip_markup())
    else:
        bot.edit_message_text( trip.update(), chat_id = trip.ch_id , message_id = trip.m_id, reply_markup = new_trip_markup(), parse_mode= "Markdown")
    
def set_price (m):
    
    price = m.text
    
    bot.delete_message(m.chat.id,m.message_id) 
    bot.delete_message(m.chat.id,m.message_id - 1)  
    
    if price.isdigit():
        trip = trip_dict[m.chat.id]
        trip.price.append(price)        
        
        if trip.pic:
            bot.edit_message_caption(caption= trip.update(), chat_id = trip.ch_id , message_id = trip.m_id, parse_mode="Markdown", reply_markup=new_trip_markup())
        else:
            bot.edit_message_text( trip.update(), chat_id = trip.ch_id , message_id = trip.m_id, reply_markup = new_trip_markup(), parse_mode= "Markdown")
    else:
        msg = bot.send_message(m.chat.id, "Укажите цену цифрами:")
        bot.register_next_step_handler(msg, set_price)

def set_pic (m):
    
    trip = trip_dict[m.chat.id]
    bot.delete_message(m.chat.id,m.message_id) 
    bot.delete_message(m.chat.id,m.message_id - 1)     
    
    if (m.photo):
        pic = m.photo[0].file_id
        trip.pic = pic 
        bot.delete_message(trip.ch_id,trip.m_id)
        bot.send_photo(m.chat.id, pic , caption= trip.update(), reply_markup = new_trip_markup(), parse_mode="Markdown")
        
    else :
        bot.edit_message_text( trip.update(), m.chat.id ,m.message_id - 2, reply_markup = new_trip_markup(), parse_mode= "Markdown")
    
'''
    Inline keyboards markups
'''        
def start_markup():
    markup = InlineKeyboardMarkup()
    
    markup.add(InlineKeyboardButton('Создать поездку',callback_data = 'add'))
    markup.add(InlineKeyboardButton('Поездки',callback_data = 'trips'))
    
    return markup


def new_trip_markup():
    
    markup = InlineKeyboardMarkup()
    
    markup.add(InlineKeyboardButton('Заголовок',callback_data = 'title'),
               InlineKeyboardButton('Дата',callback_data = 'dates'),
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
#        print ('ENTERED')
        for k in trips:
            print (trips[k]['id'], type (trips[k]['id']))
            markup.add(InlineKeyboardButton(trips[k]['title'], callback_data = trips[k]['id'])) #str(trips[k]['id'])
    
    elif key == 'reg':
        print (trips.keys())
        for k in trips['price'][1:]:
            markup.add(InlineKeyboardButton(f'Register for: {k}', callback_data = k))
            print (k, type(k))
        markup.add(InlineKeyboardButton('Назад', callback_data = 'restart'))
        
    else:
        for k in trips:
            markup.add(InlineKeyboardButton(trips[k], callback_data = trips[k]))
        
    return markup

#def get_trip_info_markup(trips):
#    markup = InlineKeyboardMarkup()
#    
#    for key in trips:
#        markup.add(InlineKeyboardButton(trips[key]['title'], callback_data = trips[key]['title']))
#        
#    return markup

'''
    Handlers
''' 
@bot.message_handler(commands=['start'])
def start_func (m):
    
    ch_id = str (m.chat.id)
    
    if ch_id in admins:        
        
        bot.send_message(ch_id, "ADMIN buttons", reply_markup = start_markup())
        
#        msg = bot.send_message(m.chat.id,  'Tell me smth') 
#        bot.register_next_step_handler(msg, del_msg) 
        
    else:
        pass

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):   
   
    ch_id = call.message.chat.id
    msg_id = call.message.message_id
    
    if call.data == "trips":                
        trips = Trip.get_list()
        bot.delete_message(ch_id,msg_id)
        bot.send_message(ch_id, 'Актуальные поездки: ', reply_markup = get_trips_markup(trips, 'title'), parse_mode="Markdown") 
      
    elif call.data == "add":   
        bot.delete_message(ch_id,msg_id)
        trip = Trip (ch_id) 
        trip_dict[ch_id] = trip
        bot.send_message(ch_id, trip.event, reply_markup = new_trip_markup(), parse_mode="Markdown")      

#re.match('\d{14}', call.data): #re.fullmatch('\*.+\*', call.data): 
    elif re.match('\d{14}', call.data):    # обработка кнопок с 
        trips = Trip.get_list()
#        print (trips, '\n\n\n') 
        trip = {}
        for n in trips:
#            print (call.data, trips[n]['id'], call.data in trips[n]['id'])
            if call.data in trips[n]['id']:
                trip = trips[n]
                trip_dict[ch_id] = trip
                
#                print (trip)
                msg = f'{trip["title"]}\n{trip["date"]}\n{trip["cond"]}\n{trip["price"]}'
#                print (msg)
                bot.delete_message(ch_id,msg_id)
#                get_trips_markup(trip, 'reg')
                
                bot.send_photo(ch_id, trip["pic"] , caption = msg, reply_markup = get_trips_markup(trip, 'reg'), parse_mode="Markdown")    
        
    elif call.data == "restart":     
         bot.delete_message(ch_id,msg_id)
#         bot.send_message(ch_id, 'Актуальные поездки: ', reply_markup = get_trips_markup(trips, 'title')) 
         bot.send_message(ch_id, "ADMIN buttons", reply_markup = start_markup())
       
        
    else:
        trip = trip_dict[ch_id]    
        trip.m_id = msg_id 
    
    
    if re.match('\d{4}|\d{3}', call.data):   # обработка кнопки с ценами
        print ('do smth')
        
    if call.data == "title":  
                     
        msg = bot.send_message(ch_id, "Enter new title:")
        bot.register_next_step_handler(msg, set_title)
    
    if call.data == "dates":   
#        trip = trip_dict[ch_id]               
        msg = bot.send_message(ch_id, "New data:")
        bot.register_next_step_handler(msg, set_date)
    
    if call.data == "descr":  
#        trip = trip_dict[ch_id]               
        msg = bot.send_message(ch_id, "New description:")
        bot.register_next_step_handler(msg, set_descr)
    
    if call.data == "pic":     
#        trip = trip_dict[ch_id]               
        msg = bot.send_message(ch_id, "New picture:")
        bot.register_next_step_handler(msg, set_pic)
        
    if call.data == "cond":     
#        trip = trip_dict[ch_id]               
        msg = bot.send_message(ch_id, "Условия поездки:")
        bot.register_next_step_handler(msg, set_cond)
        
    if call.data == "price":     
#        trip = trip_dict[ch_id]               
        msg = bot.send_message(ch_id, "Price:")
        bot.register_next_step_handler(msg, set_price)
    
        
    if call.data == "post":     
#        trip = trip_dict[ch_id] 
        bot.delete_message(trip.ch_id,trip.m_id)  
        
        if trip.pic:
            bot.send_photo(channel_id, trip.pic , caption = trip.update())
        
        else:
            bot.send_message(channel_id, trip.update())
        
        trip.upload()
        
        bot.send_message(ch_id, "ADMIN buttons", reply_markup = start_markup())
        
   
#--------------------------------------------------------------------------------------  

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    bot.reply_to(message, "still working")
    
        
bot.polling()
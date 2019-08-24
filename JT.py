# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 22:50:35 2019

@author: alexu
"""
from jsonDB import DB

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '989604812:AAE1NWU3CwhDfo41ucg80nE2aboimTmlDtQ'

bot = telebot.TeleBot(API_TOKEN)

user_dict = {}
trip_dict = {}

channel_id = '@prj360Test' #-1001205642456 

f = DB('DB.json')

def gen_markup(text, answ = None, link=None):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(text, callback_data=answ, url= link))
    return markup

class User:
    def __init__(self, ch_id):
        self.chat = ch_id
        self.name = None
        self.phone = None
        self.tg = False
        
    def __str__ (self):
        print (self.name, self.phone , self.tg )
        
class Trip:
    def __init__(self,trip_id):
        self.trip_id = ''
        self.title = 'EVENT'
        self.date = 'Дата: '
        self.descr = 'DEFAULT'
        self.pic = None
        self.price = 'bagato'
        self.event = ''
        self.members = {}
        
    def __str__ (self):
        print (self.title, self.dates , self.price )

    def get_all (self):
        self.event = f'{self.title} \n {self.date}\n{self.descr}\n{self.price}\nЗаписывайтесь у нашего бота -> @prjTestBot'
        return self.event

@bot.message_handler(commands=['addTrip'])
def create_trip (m):
    msg = bot.send_message(m.chat.id, """\
    Код поездки: 
    """)
    bot.register_next_step_handler(msg, set_id)   

def set_id (m):
    trip_id = m.text
    trip = Trip (trip_id)
    trip_dict[m.chat.id] = trip
    msg = bot.reply_to( m, """\
    title: 
    """)
    bot.register_next_step_handler(msg, set_title) 

def set_title (m):
    title = m.text
    trip = trip_dict[m.chat.id]
    trip.title = title
    msg = bot.reply_to( m, """\
    dates: 
    """)
    bot.register_next_step_handler(msg, set_date) 

def set_date (m):
    date = m.text
    trip = trip_dict[m.chat.id]
    trip.date += date
    msg = bot.reply_to( m, """\
    Description: 
    """)
    bot.register_next_step_handler(msg, set_descr) 

def set_descr (m):
    descr = m.text
    trip = trip_dict[m.chat.id]
    trip.descr = descr
    msg = bot.reply_to( m, """\
    Prices: 
    """)
    bot.register_next_step_handler(msg, set_price) 

def set_price (m):
    price = m.text
    trip = trip_dict[m.chat.id]
    trip.price = price
    msg = bot.reply_to( m, """\
    Send picture: 
    """)
    bot.register_next_step_handler(msg, set_pic) 

def set_pic (m):
    
    trip = trip_dict[m.chat.id]
    msg =  trip.get_all()
    
    
    if (m.photo):
        pic = m.photo[0].file_id
        trip.pic = pic
        keyboard = gen_markup("Постим?", "photo")
        bot.send_photo(m.chat.id, pic , caption= msg, reply_markup = keyboard)
        
    else :
        keyboard = gen_markup("Постим?", "msg")
        bot.send_message(m.chat.id, msg, reply_markup = keyboard)


@bot.message_handler(commands=['test'])
def get_tris (m):
#    trip = Trip('smth')
    msg = bot.send_message(m.chat.id,  'Tell me smth') 
    bot.register_next_step_handler(msg, del_msg) 
    
def del_msg(m):
    print (m)
    bot.delete_message(m.chat.id,m.message_id)
    bot.send_message(m.chat.id, "I deleted your message")
  
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    
    ch_id = call.message.chat.id
    trip = trip_dict[ch_id]
    
    if call.data == "photo":   
        
        bot.send_photo(channel_id, trip.pic , caption= trip.event)
        
    if call.data == "msg":
        bot.send_message(channel_id, trip.event)
    
#
#@bot.message_handler(commands=['help', 'start'])
#def send_welcome(message):
#    msg = bot.reply_to(message, """\
#Hi there, I am Example bot.
#What's your name?
#""")
#    bot.register_next_step_handler(msg, process_name_step)
#
#
#def process_name_step(message):
#    try:
#        chat_id = message.chat.id
#        name = message.text
#        user = User(name)
#        user_dict[chat_id] = user
#        msg = bot.reply_to(message, 'How old are you?')
#        bot.register_next_step_handler(msg, process_age_step)
#    except Exception as e:
#        print (e)
#        bot.reply_to(message, 'oooops')
#        
#def process_age_step(message):
#    try:
#        chat_id = message.chat.id
#        age = message.text
#        if not age.isdigit():
#            msg = bot.reply_to(message, 'Age should be a number. How old are you?')
#            bot.register_next_step_handler(msg, process_age_step)
#            return
#        user = user_dict[chat_id]
#        user.age = age
#        markup = ReplyKeyboardMarkup(one_time_keyboard=True)
#        markup.add('Male', 'Female')
#        msg = bot.reply_to(message, 'What is your gender', reply_markup=markup)
#        bot.register_next_step_handler(msg, process_sex_step)
#    except Exception as e:
#        print (e)
#        bot.reply_to(message, 'oooops')
#
#
#def process_sex_step(message):
#    try:
#        chat_id = message.chat.id
#        sex = message.text
#        user = user_dict[chat_id]
#        if (sex == u'Male') or (sex == u'Female'):
#            user.sex = sex
#        else:
#            raise Exception()
#        bot.send_message(channel_id, 'Nice to meet you ' + user.name + '\n Age:' + str(user.age) + '\n Sex:' + user.sex)
#    except Exception as e:
#        print (e)
#        bot.reply_to(message, 'oooops')        
#        
#        
#@bot.message_handler(func=lambda message: True)
#def message_handler(message):
#    bot.send_message(message.chat.id, "ENTERED")


#    
#bot.send_photo(m.chat.id, 'AgADAgAD2qsxG65y0UqVItAnbC5QWcD0ug8ABAEAAwIAA20AA18LAQABFgQ', caption=None)        
#

bot.polling()
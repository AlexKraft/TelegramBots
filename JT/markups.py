# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 12:14:06 2019

@author: pc
"""

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

'''

    Inline keyboards markups
    
'''        
def start_markup(ch_id):
    
    markup = InlineKeyboardMarkup()
    
    markup.add(InlineKeyboardButton('Создать поездку',callback_data = 'add'))
    markup.add(InlineKeyboardButton('Поездки',callback_data = 'trips'))
    
#    bot.send_message(ch_id, "ADMIN buttons", reply_markup = markup)
    
    return markup

def gen_markup(db, key = None):
    
    markup = InlineKeyboardMarkup()   
    
    if key == 'trips_list':
        trips = db['trips']   
        for k in trips:
            
            trip = trips[k]['title']
            
            print ('trips_list:>>>>>',trip, '  id - ',k)
            markup.add(InlineKeyboardButton(trip, callback_data = k)) #str(trips[k]['id'])
    
    elif key == 'new_trip':
        markup.add(InlineKeyboardButton('Заголовок',callback_data = 'title'),
                   InlineKeyboardButton('Дата',callback_data = 'date'),
                   InlineKeyboardButton('Описание',callback_data = 'descr'),
                   InlineKeyboardButton('Фото',callback_data = 'pic'),
                   InlineKeyboardButton('Условия',callback_data = 'cond'),
                   InlineKeyboardButton('Цена',callback_data = 'price'))
   
        markup.add(InlineKeyboardButton('Постим?',callback_data = 'post'))
        
    elif key == 'register':
        print ('get_trips_markup<<<<<<<reg<<<<<<<<<<',trips.keys())
        for k in trips['price']:
            markup.add(InlineKeyboardButton(f'Register for: {k}', callback_data = 'reg' + k))
            print (k, type(k))
        markup.add(InlineKeyboardButton('Назад', callback_data = 'restart'))
        
    else:
        print ('get_trips_markup<<<<<<<else<<<<<<<<<<')
#        for k in trips:
#            markup.add(InlineKeyboardButton(trips[k], callback_data = trips[k]))
            
    markup.add(InlineKeyboardButton('Назад', callback_data = 'back'))    
    
    return markup

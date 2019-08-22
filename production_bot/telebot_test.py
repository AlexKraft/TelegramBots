# -*- coding: utf-8 -*-


import telebot
import random, time, apscheduler, json

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from datetime import date

from apscheduler.schedulers.blocking import BlockingScheduler


#sched = BlockingScheduler()
#sched.start()

API_TOKEN = '917496386:AAEf9CIT4PAxlU60TXA-zt4z2ipZDwVlBi4'

# only used for console output now
#def listener(messages):
#   
#    for m in messages:
#        if m.content_type == 'text':
#            # print the sent message to the console
#            print(f'\n\n\n{str(m.chat.first_name)} [{str(m.chat.id)}]: {m.text}\n\n')

bot = telebot.TeleBot(API_TOKEN)
#bot.set_update_listener(listener)  # register listener



fortune = ['Определенно', 'Похоже на то', 'Без сомнений',
           "Определенно ДА","Похоже на то", "Звучит неплохо",
           "Да","Все указывает на ДА",
           "Как-то неуверенно, попробуй снова","Спроси позже", "Я лучше не буду отвечать сейчас",
           "Щас не готов ответить","Ты это, конкретнее вопрос задай",
           "Я б на это не расчитывал","Ответ НЕТ", "Мои источники говорят что нет",
           "Выглядит хреново","Очень сомнительно"]

def showInlineKeyBoard():
    print("InlineFunct!!!!")

    reply_markup = ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True, row_width = 1)
    reply_markup.add('Ask Oracle','Поел')
#    reply_markup.add('Поел')
    
    return reply_markup



def hideInlineKeyBoard():
    hideBoard = ReplyKeyboardRemove()
    return hideBoard

def alarm_notification (cid):
    bot.send_message(cid, "Ты попросил напомнить")
    

# handle the "/start" command
@bot.message_handler(commands=['start','help'])
def command_start(m):
    cid = m.chat.id
    
    bot.send_message(cid, "Отвечаю на вопросы.\nТак что задай вопрос")#, reply_markup=showInlineKeyBoard()

#
#@bot.message_handler(func=lambda message: message.text == 'Поел')
def set_alarm(m):
    cid = m.chat.id   
    sched = BlockingScheduler()
    s = m.text
    k = time.strftime('%Y-%m-%d %H:%M:%S',(time.localtime(time.time() + int(s))))
    sched.add_job(alarm_notification, 'date', run_date= k, args=[cid])
    
   
    bot.send_message(cid, "Ок, я напомню как придет время")
    
    sched.start()


#@bot.message_handler(func=lambda message: message.text == 'Ask Oracle')
#def message_reply(message):    
#    bot.send_message(message.chat.id, random.choice(fortune))
    
@bot.message_handler(commands=['set'])
def alarm (m):
    msg = bot.reply_to(m, """\
    Через сколько секунд тебе напомнить?
    """)
    bot.register_next_step_handler(msg, set_alarm)    
    
    
@bot.message_handler(regexp=r'\?')
def send_ans(message):    
    bot.send_message(message.chat.id, random.choice(fortune))
    
@bot.message_handler(content_types=['photo'])
def sm_func(m):
    print (m)

@bot.message_handler(func=lambda message: True)
def message_handler(m):
    print (m.json)
    bot.send_message(m.chat.id, "I don't understand \"" + m.text + "\"\nMaybe try the help page at /help")
    
   
bot.polling()
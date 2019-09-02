import telebot, json
import geopy.distance
'''
text, audio, document, photo, sticker, video, video_note, voice, location, contact, 
new_chat_members, left_chat_member,
new_chat_title, 
new_chat_photo, delete_chat_photo, 
group_chat_created, supergroup_chat_created, 
channel_chat_created, migrate_to_chat_id, migrate_from_chat_id, 
pinned_message
'''

API_TOKEN = '989604812:AAE1NWU3CwhDfo41ucg80nE2aboimTmlDtQ'

bot = telebot.TeleBot(API_TOKEN)

voice = None

def load_dummy():
    dummy = json.load(open('dist.json', "r"))
    return dummy

def dump_dummy(dummy):
    json.dump(dummy , open('dist.json', "w+"), indent = 2, ensure_ascii=False)
    
@bot.message_handler(commands=['test'])
def st_func (m):    
    bot.forward_message(383621032, -1001262590723, 252)
       

@bot.message_handler(func=lambda m: True)
def fish(m):
    print ('\njust text\n',m)    
    pass

@bot.message_handler(content_types=['photo'])
def photo(m):
    print ('\nphoto try\n',m)
    pass
   
@bot.message_handler(content_types=['voice'])
def message_handler(message):
    global voice
    voice = message.voice
    bot.reply_to(message, "still working")


def some_func(m, start_coord):
    
    end_coords = [m.location.latitude,m.location.longitude]
    print (f'End:\n{end_coords}')
    
    print (geopy.distance.distance(start_coord, end_coords).m)
    
@bot.message_handler(content_types=['location'])
def location(m):
    
    ch_id = str(m.chat.id) 
    
    dummy = load_dummy()
    
    if not dummy['msg']:
        bot.send_location(ch_id, dummy['coords'][0][0], dummy['coords'][0][1], live_period = 60*60)
        msg_id = m.message_id + 1
        print (m.message_id, '\n', msg_id)
        dummy['msg'] = msg_id
        dump_dummy(dummy)
    
        bot.send_message(ch_id, "You need to follow me to get food!!!")
        
    else:        
        bot.send_message(ch_id, "You need to follow me to get food!!!")
                
                
@bot.edited_message_handler(content_types=['location'])
def location_edit(m):
    
    ch_id = str(m.chat.id)  
    coords = (m.location.latitude,m.location.longitude)
    
    
    dummy = load_dummy()
    next_point = dummy['coords'][0]
    msg_id = dummy['msg']
    
        
    Distance = geopy.distance.distance(coords, next_point).m    
    
    if Distance <= 50:
        dummy['coords'].pop(0)
        dump_dummy(dummy)
        
        if dummy['coords']:            
            bot.send_message(ch_id, "You're getting closer, go to next point")
            bot.edit_message_live_location(dummy['coords'][0][0], dummy['coords'][0][1], chat_id=ch_id, message_id=msg_id)
        
        else:
            bot.send_message(ch_id, "You've maid it")
            dummy['msg'] = None
            dump_dummy(dummy)
            bot.delete_message(ch_id,msg_id)
            
            
#@bot.message_handler(commands=['test'])
#def st_func (m):  
#    
#    dummy = load_dummy()
#    msg = 'Coords left:\n'
#    for item in dummy:
#        msg+= ''.join(item),'\n'
'''
[[50.436537, 30.431367],
 [50.437541, 30.431456],
 [50.439784, 30.433261],
 [50.440164, 30.435021]]
'''            
#@bot.message_handler(commands=['test'])
#def st_func (m):  
#    
#    dummy = load_dummy()
#    new_dummy = {'coords': dummy}
#    new_dummy['msg'] = None
#    
#    dump_dummy(new_dummy)

bot.polling()
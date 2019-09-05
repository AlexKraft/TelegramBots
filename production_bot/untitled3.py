

 
msg = db['game']['text_list'] if db['game']['active'] else "Жди уведомление, пока что нет активных игр"
markup = gen_markup(db, 'show',ch_id)) if ch_id in db["admin"] else gen_markup(db, 'new_player',ch_id) 



if ch_id in db["admin"]: 
            if db['game']['active']:                
                bot.send_message(chat_id = ch_id, 
                                  text = db['game']['text_list'], 
                                  reply_markup = gen_markup(db, 'show',ch_id))                
            else:
                bot.send_message(chat_id = ch_id, 
                                  text = "Че надо?", 
                                  reply_markup = gen_markup(db, 'create'))
        else:
            if db['game']['active']:
                if ch_id in db['game']['players']:
                    bot.send_message(chat_id = ch_id, 
                                     text = db['game']['text_list'])
                    db["game"]["players"][ch_id] = str (msg_id + 1)
                    
                else:
                    bot.send_message(chat_id = ch_id, 
                                     text = db['game']['text_list'],
                                     reply_markup = gen_markup(db, 'new_player'))                    
            else:
                bot.send_message(chat_id = ch_id, 
                                 text = "Жди уведомление, пока что нет активных игр")
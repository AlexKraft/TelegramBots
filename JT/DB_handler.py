
import json
from datetime import datetime

def load_dummy():
    dummyDB = json.load(open('dummy.json', "r"))
    return dummyDB

def dump_dummy(dummyDB):
    json.dump(dummyDB , open('dummy.json', "w+"), indent = 2, ensure_ascii=False)



def loadDB():
    db = json.load(open('trips.json', "r"))
    return db


def newUserDB(db):
    json.dump(db, open('trips.json', "w+"), indent = 2, ensure_ascii=False)
    
def dumpDB(dummy):
    db = loadDB()
    trip_id = datetime.today().strftime("%Y%m%d%H%M%S")
    dummy['active'] = True       
    
    for price in dummy['price']:
        dummy['members'][price] = []
        
    db['trips'][trip_id] = dummy  
    
    
    json.dump(db, open('trips.json', "w+"), indent = 2, ensure_ascii=False)



def update(trip):
    
    tail = '\nЗаписывайтесь у нашего бота -> @prjTestBot\nИли по телефону ..................'
    
    
    if len(trip['price']) == len(trip['cond']):
        price = ''
        for elem in range(len(trip['price'])):
            
            num,des = ''.join(trip['price'][elem]),''.join(trip['cond'][elem])
            price += f'_{num}_ грн - {des}\n'
            
        trip['event'] = f"*{trip['title']}*\n\nДата: {trip['date']}\n\n{trip['descr']}\n\n*Цена:*\n{price}\n{tail}"
    else:
        price  = ' грн\n'.join(trip['price'])
        cond  = '\n'.join(trip['cond'])
        trip['event'] = f"*{trip['title']}*\n\nДата: {trip['date']}\n\n{trip['descr']}\n{cond}\n\n*Цена:*\n_{price}_{tail}"
   
    return trip['event']
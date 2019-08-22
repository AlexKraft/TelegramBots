# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 15:18:14 2019

@author: pc
"""

import pickle 


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
        print (self.title, self.date , self.price )

    def get_all (self):
        self.event = f'{self.title} \n {self.date}\n{self.descr}\n{self.price}\nЗаписывайтесь у нашего бота -> @prjTestBot'
        return self.event


obj = Trip('0001')

#print (obj.get_all())

obj.title = "New title"
obj.date += "20.08"
obj.descr = "NO!!!"
obj.price = "+100500"

f = open('file.txt', 'w+') 

#f.write(str(obj))

#pickle.dump(obj, f)
f.close()

file_pi2 = open('file.txt', 'r') 
#object_pi2 = file_pi2.read(file_pi2)
object_pi2 = pickle.load(file_pi2)

print (object_pi2.title)
print (object_pi2.date)
print (object_pi2.descr)
print (object_pi2.price)

print (obj.get_all())
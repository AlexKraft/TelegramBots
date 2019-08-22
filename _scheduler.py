# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 12:43:02 2019

@author: pc
"""

#------------------------------------------------------------------------
from threading import Timer

def hello():
    print "hello, world"

t = Timer(30.0, hello)
t.start()  # after 30 seconds, "hello, world" will be printed


#------------------------------------------------------------------------
'''
Triggers at ocuring smth, as in examle when second=0 so every minute


    year (int|str) – 4-digit year

    month (int|str) – month (1-12)

    day (int|str) – day of the (1-31)

    week (int|str) – ISO week (1-53)

    day_of_week (int|str) – number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)

    hour (int|str) – hour (0-23)

    minute (int|str) – minute (0-59)

    second (int|str) – second (0-59)

    start_date (datetime|str) – earliest possible date/time to trigger on (inclusive)

    end_date (datetime|str) – latest possible date/time to trigger on (inclusive)

    timezone (datetime.tzinfo|str) – time zone to use for the date/time calculations (defaults to scheduler timezone)

    jitter (int|None) – advance or delay the job execution by jitter seconds at most.


*       any     Fire on every value
*/a     any     Fire every a values, starting from the minimum
a-b     any     Fire on any value within the a-b range (a must be smaller than b)
a-b/c   any     Fire every c values within the a-b range
xth y   day     Fire on the x -th occurrence of weekday y within the month
last x  day     Fire on the last occurrence of weekday x within the month
last    day     Fire on the last day within the month
x,y,z   any     Fire on any matching expression; can combine any number of any of the above expressions


'''
def job_function():
    print("Hello, world")

from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.start()
# Schedules job_function to be run on the third Friday
# of June, July, August, November and December at 00:00, 01:00, 02:00 and 03:00
sched.add_job(job_function, 'cron', month='6-8,11-12', day='3rd fri', hour='0-3')
# Schedules job_function to be run every minute
scheduler.add_job(job_function, trigger='cron', second=0)
# Runs from Monday to Friday at 5:30 (am) until 2014-05-30 00:00:00
sched.add_job(job_function, 'cron', day_of_week='mon-fri', hour=5, minute=30, end_date='2014-05-30')

#decorator
@sched.scheduled_job('cron', id='my_job_id', day='last sun')
def some_decorated_task():
    print("I am printed at 00:00:00 on the last Sunday of every month!")

#------------------------------------------------------------------------
sched = BlockingScheduler()

# Schedule job_function to be called every two hours
sched.add_job(job_function, 'interval', hours=2)

sched.start()

# The same as before, but starts on 2010-10-10 at 9:30 and stops on 2014-06-15 at 11:00
sched.add_job(job_function, 'interval', hours=2, start_date='2010-10-10 09:30:00', end_date='2014-06-15 11:00:00')
#--------------------------------------
from apscheduler.scheduler import BlockingScheduler

@sched.scheduled_job('interval', id='my_job_id', hours=2)
def job_function():
    print("Hello World")
    
# Run the `job_function` every hour with an extra-delay picked randomly in a [-120,+120] seconds window.
sched.add_job(job_function, 'interval', hours=1, jitter=120)



#-------------------------------------------------------
from datetime import date

from apscheduler.schedulers.blocking import BlockingScheduler


sched = BlockingScheduler()

def my_job(text):
    print(text)

# The job will be executed on November 6th, 2009
sched.add_job(my_job, 'date', run_date=date(2009, 11, 6), args=['text'])

sched.start()

'''
import time

t = time.time() + secs
tl = time.localtime(a)
tstring = time.strftime('%Y-%m-%d %H:%M:%S',tl)

#'2019-08-13 13:29:30'




from datetime import datetime, date, time

datetime.now()
>>>> datetime.datetime(2019, 8, 19, 15, 55, 36, 875061)

'''

# The job will be executed on November 6th, 2009 at 16:30:05
sched.add_job(my_job, 'date', run_date=datetime(2009, 11, 6, 16, 30, 5), args=['text'])

sched.add_job(my_job, 'date', run_date='2009-11-06 16:30:05', args=['text'])

# The 'date' trigger and datetime.now() as run_date are implicit
sched.add_job(my_job, args=['text'])

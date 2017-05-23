import threading
import os
import datetime
import time


def go(t1):
    """ Таймер """
    while True:
        print("Time of voting is 1 minutes:")
        my_time = datetime.datetime.now() - t1
        str_time = str(my_time).split(':')
        str_sec = str_time[2].split('.')
        print(str_time[0],":",str_time[1],":",str_sec[0])
        time.sleep(0.9)
        os.system('cls')
        if float(str_time[2]) > 58 and float(str_time[1]) == 1 :
            return

def start_timer(time_for_vote):
    """ Запуск таймера в отдельном потоке """
    t = threading.Thread(target=go, kwargs={'t1': time_for_vote})
    t.start()
    return t
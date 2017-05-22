import threading
import os
import datetime
import time

class TimeIsEndException(BaseException):
    def __init__(self):
        TimeIsEndException.text = "Time is over!"


def go(t1):
    while True:
        print("Time of voting is 1 minutes:")
        my_time = datetime.datetime.now() - t1
        print(my_time)
        str_time = str(my_time).split(':')
        time.sleep(0.9)
        os.system('cls')
        if float(str_time[2]) > 20:
            return TimeIsEndException

def start_timer(time_for_vote):
    t = threading.Thread(target=go, kwargs={'t1': time_for_vote})
    t.start()
    return t
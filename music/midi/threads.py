from threading import Timer
import time

def sprout(func, *args):
    t = Timer(0., func, args)
    t.start()
    return t

def delayed_sprout(func, delay, *args):
    t = Timer(delay, func, args)
    t.start()
    return t

class WaitClass:
    now = time.time()
    def wait(self, duration):
        curtime = time.time()
        time.sleep(duration - (curtime - self.now))
        self.now = time.time()

wait  = WaitClass().wait
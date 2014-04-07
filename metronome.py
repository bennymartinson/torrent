from threading import Event, Thread
from time import time, sleep
import math

class _Metronome(Thread):
    start_time = 0
    start_offset = round(time())
    events = None
    has_beat = False
    beat_min = 0.1
    beat_max = 0.4
    beat = 0
    
    def __init__(self):
        self.start_time = time()
        self.events = []
        Thread.__init__(self)
        self.start()
        
    def now(self):
        return time() - self.start_time
    
    def schedule(self, time, function, args=(),):
        self.events.append((time, function, args),)
        self.events.sort()

    def run(self):
        self.running = True
        while self.running:
            while len(self.events) and self.now() >= self.events[0][0]:
                self.events[0][1](*self.events[0][2])
                self.events = self.events[1:]
            sleep(0.01)

metronome = _Metronome()

class Wait():
    event = None
    def __init__(self, evtTime):
        self.event = Event()
        metronome.schedule(evtTime, self.finish)
        self.wait()
    
    def wait(self):
        self.event.wait()
    
    def finish(self):
        self.event.set()

wait_until = Wait


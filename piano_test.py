from global_vars import min_piano_dur, min_piano_up, midi
from utilities import route
import effects
import time


# needs .2
min_piano_dur = 0.2
min_piano_up = 0.01
def test1():
    velocity = 0
    pitch = 60
    for x in range(1000):
        midi.note(pitch, min_piano_dur, velocity)
        time.sleep(min_piano_dur + min_piano_up)

def test2():
    for velocity in range(0,127):
        midi.note(60, 0.5, velocity)
        print velocity
        time.sleep(1)
    
def test3():
    echo = effects.Echo()
    route(echo, midi)
    midi.setSustain(True)
    velocity = 100
    for x in range(1000):
        pitch = 60 + x
        echo.note(pitch, 0.1, velocity)
        time.sleep(0.15)

'''
midi.note(60, 1, 64, 1)
time.sleep(2)'''
test1()
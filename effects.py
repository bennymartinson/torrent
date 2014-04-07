from global_vars import midi, min_piano_dur
import warnings
import random
import time
from utilities import constrain, sprout, route
#import operator
import math

class Effect:
    """Abstract class for effects."""
    midi_out = None
    def __init__(self, midi_out=None, **kwargs):
        self.midi_out = midi_out
        for k,v in kwargs.items():
            setattr(self, k, v)
    
    def note(self, pitch=60, dur=1, velocity=80, layer=0, keycode=None):
        if self.midi_out is None:
            warnings.warn("No midi out was set for the object {}. Ignoring note message.".format(self))
            return
        sprout(self._in, pitch, dur, velocity, layer, keycode)
    
    def _in(self, pitch=60, dur=0.25, velocity=64, layer=0, keycode=None):
        """ A sprouted function which takes processes and sends on MIDI messages."""
    
    def _out(self, pitch=60, dur=0.25, velocity=64, layer=0, keycode=None):
        """Target for sending notes out within the _in function"""
        if self.midi_out is None:
            self.midi_out = midi
            warnings.warn("The midi out object is missing.  Defaulting to midi controller.")
        self.midi_out.note(pitch, dur, velocity, layer, keycode)

class Humanize(Effect):
    delay_max = 0.03
    velocity_max = 20
    
    def _in(self, pitch, dur, velocity, layer=0, keycode=None):
        vel_range = self.velocity_max/2
        velocity = constrain(velocity + random.randint(-vel_range, vel_range), 1, 127)
        time.sleep(random.randint(0, 5)/5. * self.delay_max)
        self._out(pitch, dur, velocity, layer, keycode)

class Octaves(Effect):
    span = 2
    decay = 0.5
    def _in(self, pitch, dur, velocity, layer=0, keycode=None):
        octaves_above = int(math.ceil(self.span/2.))
        octaves_below = int(math.floor(self.span/2.))
        
        self._out(pitch, dur, velocity, layer, keycode)
        for i in range(octaves_above):
            self._out(pitch+12*(i+1), dur, int(velocity*(self.decay**(i+1))), layer, keycode)
        for i in range(octaves_below):
            self._out(pitch-12*(i+1), dur, int(velocity*(self.decay**(i+1))), layer, keycode)

class Echo(Effect):
    next_velocity = None
    decay = 0.85
    delay = 0.2
    decay_variability = 0.1
    shift_direction = False
    shift_type = 'wholestep'
    harmonic_series = [0, 12, 19, 24, 28, 31, 34, 36, 38, 40, 42, 43]
    
    def _in(self, pitch, dur, velocity, layer, keycode):
        step = 0
        decay = self.decay + self.decay_variability*random.randint(-5,5)*0.2
        while velocity > 1:
            t = time.time()
            pitch += self._get_upward_displacement(step)
            self._out(pitch, max(self.delay - min_piano_dur, min_piano_dur), velocity, layer, keycode)
            step+=1
            velocity = int(velocity * decay)
            time.sleep(self.delay + t - time.time())
    
    def _get_upward_displacement(self, step):
        if not self.shift_direction:
            return 0
        elif self.shift_direction == 'random':
            if self.shift_type == 'octave':
                step = random.randint(-2,2)
            elif self.shift_type == 'harmonic':
                step = random.randint(0,11)
            elif self.shift_type == 'wholestep':
                step = random.randint(-6,6)
        
        if self.shift_type == 'harmonic':
            if step >= len(self.harmonic_series):
                return self.harmonic_series[-1]
            return self.harmonic_series[step]
        elif self.shift_type == 'octave':
            return step * 12
        elif self.shift_type == 'wholestep':
            return step * 2
        elif self.shift_type == 'halfstep':
            return step

class Glissando(Effect):
    amt = 0.1
    
    def chord(self, pitches, dur, velocity, layer=0, keycode=None):
        self._out(pitches[0], dur, velocity, layer)
        if pitches > 1:
            sprout(self._chord, pitches[1:], dur, velocity, layer, keycode)
        
    def _chord(self, pitches, dur, velocity, layer, keycode):
        for pitch in pitches:
            time.sleep(self.amt)
            self._out(pitch, dur, velocity, layer, keycode)
        
    def _in(self, pitch, dur, velocity, layer, keycode=None): 
        pass #not used for this effect.

class Gain(Effect):
    vel_multiplier = 1
    def _in(self, pitch, dur, velocity, layer, keycode=None):
        velocity = int(self.vel_multiplier*velocity)
        self._out(pitch, dur, velocity, layer, keycode)
    
    def fade(self, start=0, finish=1, duration=10):
        self.vel_multiplier = start
        sprout(self._fade, start, finish, duration)
    
    def _fade(self, start, finish, duration):
        for i in range(0, 100):
            self.vel_multiplier = i * 0.01 * (finish-start) + start
            time.sleep(duration * 0.01)
        self.vel_multiplier = finish

def echos():
    print 'echoing'
    midi.setSustain(True)
    humanize = Humanize(delay_max = 0.01, velocity_max = 20)
    echo = Echo(decay=0.85, delay=0.2, decay_variability=0.1)
    gain = Gain()
    gain.fade(0,1,10)
    
    route(echo, humanize)
    route(humanize, gain)
    route(gain, midi)
    
    note_choices = [x + octave*12 for x in (4,5,7,11,12) for octave in (1,2,3,4,5,6,7,8)]
    print note_choices
    while True:
        t = time.time()
        echo.note(random.choice(note_choices), 0.15,60)
        time.sleep(random.choice((0.4,0.6)) - time.time() + t)
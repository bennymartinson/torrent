import music.midi as midi
import threading
import time
import random
import warnings
from utilities import sprout, scale
from copy import copy
import global_vars

midi = global_vars.midi
min_piano_dur = global_vars.min_piano_dur
events = global_vars.events

class Instrument:
    playing = False
    frozen = False
    ramping = False
    midi_out = None
    
    def __init__(self, pitches, velocity=80, **kwargs):
        self.pitches = list(pitches)
        self.velocity = velocity
        
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def start(self):
        self.playing = True
        sprout(self._play)
        
    def stop(self):
        self.playing = False
        
    def _play(self):
        pass
    
    def _out(self, pitch=60, dur=0.25, velocity=64, layer=0):
        if self.midi_out is None:
            self.midi_out = midi
            #warnings.warn("The midi out object is missing.  Defaulting to midi controller.")
        self.midi_out.note(pitch, dur, velocity, layer)
    
    def ramp(self, fromVel, toVel, duration):
        sprout(self._ramp, fromVel, toVel, duration)
        
    def _ramp(self, fromVel, toVel, duration):
        num_steps = duration * 10
        for x in xrange(num_steps):
            self.velocity = int(fromVel + (toVel - fromVel) * x / float(num_steps))
            time.sleep(0.1)
        self.velocity = toVel
        
class Notes(Instrument):
    def _play(self):
        for pitch in self.pitches:
            self._out(pitch, self.min_piano_dur, self.velocity)
    
    def slide(self, pitches, velocity):
        inst = copy(self)
        inst.pitches = pitches
        inst.velocity = velocity
        inst.start()
        return inst

class Echo(Instrument):
    next_velocity = None
    decay = 0.5
    delay = 0.5
    decay_variability = 0.2
    delay_variability = 0.1
    shift_direction = False
    kill_echo_on_stop = False
    shift_type = 'wholestep'
    harmonic_series = [0, 12, 19, 24, 28, 31, 34, 36, 38, 40, 42, 43]
    
    def _play(self):
        self.next_velocity = self.velocity
        step = 0
        decay = self.decay + self.decay_variability * random.randint(-5,5) * 0.2
        while self.next_velocity > 5 and (self.playing or self.kill_echo_on_stop):
            for pitch in self.pitches:
                pitch += self._get_upward_displacement(step)
                self._out(pitch, 0.15, self.next_velocity)
            
            step+=1
            self.next_velocity = int(self.next_velocity * decay)
            time.sleep(self.delay * (1 + random.randint(-10,10)*.1*self.delay_variability))
    
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
    
    def slide(self, pitches, velocity):
        inst = copy(self)
        inst.pitches = pitches
        inst.velocity = velocity
        inst.start()
        return inst

class Tremolo(Instrument):
    in_hit = False
    crescendo = True
    
    def start(self, hit=False):
        self.playing = True
        if hit:
            sprout(self._hit_play)
        else:
            sprout(self._play)
        
    def slide(self, pitches, velocity):
        """Perform necessary behavior whenever sliding and return new object"""
        in_hit = self.in_hit
        self.stop()
        inst = copy(self)
        inst.pitches = pitches
        inst.velocity = velocity
        inst.start(in_hit)
        return inst
    
    def _hit_play(self):
        self.in_hit = True
        for pitch in self.pitches:
            self._out(pitch, 0.9, self.velocity)
        sleepdur = 1.
        for _ in xrange(100):
            if not self.playing:
                for pitch in self.pitches:
                    self.midi_out.noteOff(pitch, 0)
                return None
            time.sleep(sleepdur / 100.)
        self.in_hit = False
        self._play()
    
    def _play(self):
        if self.crescendo:
            self.ramp(self.velocity, self.velocity+30, 15)
        duration = 0.
        while self.playing:
            if len(self.pitches) > 2:
                random.shuffle(self.pitches)
            for pitch in self.pitches:
                vel = scale(self.velocity, 0, 127, 10, 127)
                vel = int(self.velocity + random.randint(-5, 5))
                vel = min(max(vel, 0), 127)
                
                self._out(pitch, 0.03, vel)
                wait = 0.05 + random.randint(0, 10) / 1000.
                time.sleep(wait)
                duration += wait
                if duration > 15 and self.crescendo:
                    events.send('long_tremolo')
                    duration = 0.

if __name__ == '__main__':
    print 'here'
    mp = midi.MidiPlayer()
    mp.setSustain(True)
    tremolos = []
    for pitches in [41, 48, 55],[57, 64, 71]:
        trem = Tremolo(pitches, mp, 80)
        trem.start(hit=True)
        tremolos.append(trem)
    time.sleep(10)
    for t in tremolos:
        t.stop()
        time.sleep(1)
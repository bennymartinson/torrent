from autonomous import Autonomous
from gesture import Ictus
import random
from global_vars import events, kinect, midi
from effects import Glissando
from time import sleep
from math import floor
from utilities import scale_constrain, route
from metronome import metronome, wait_until

class Americana(Autonomous):
    chords = ( (-7, -3,  7, 12, 16),
               (-8,  0,  9, 12, 17),
               (-5,  2, 11, 16, 19),
               (-3,  4, 12, 17, 21),
               ( 0,  7, 14, 19, 23),
               ( 2,  9, 16, 21, 24),
               ( 7, 14, 17, 21, 26) )
    
    root = 60
    index = 0
    velocity = 20
    
    rhythms = None
    ictus = None
    glissando = None
    
    def _setup(self):
        self.ictus = Ictus()
        self.rhythms = []
        self.glissando = Glissando(amt=0.05)
        route(self.glissando, self)
        for pitch in self.get_chord():
            r = Rhythm(pitch=pitch, beat=0.15)
            self.rhythms.append(r)
    
    def _start(self):
        self.ictus.detect('ictus')
        for r in self.rhythms:
            r.play()
    
    def _play(self):
        events.wait_for('ictus')
        height = kinect.get_coord('righthand')[1]
        index = int(height / 70)
        self.index = index
        self.velocity = (scale_constrain(self.ictus.avg_magnitude, 15, 130, 10, 100) * .5
                         + self.velocity * .5)
        
        pitches = self.get_chord()
        self.set_pitches(pitches, self.velocity)
        
        self.glissando.amt = 6/max(6,self.ictus.magnitude) * 0.1 # faster gliss with faster ictus
        self.glissando.chord([p-12 for p in pitches], 3, min(self.velocity+15,127))
    
    def _stop(self):
        self.ictus.stop()
        for r in self.rhythms:
            r.stop()
            midi.unlockPitch(r.pitch)
    
    def get_chord(self):
        octaves = int(floor(self.index / len(self.chords)))
        index = self.index % len(self.chords)
        displacement = octaves*12+self.root
        return [pitch+displacement for pitch in self.chords[index]]
    
    def set_pitches(self, pitches, velocity):
        for pitch, rhythm in zip(pitches, self.rhythms):
            midi.unlockPitch(rhythm.pitch)
            rhythm.pitch = pitch
            midi.lockPitch(rhythm.pitch, 'rhythm')
            rhythm.loud = min(max(velocity+10,20),127)
            rhythm.quiet = min(max(velocity-20, 10),100)

class Rhythm(Autonomous):
    beat  = 0.2
    pitch = 62
    rhythm = None
    loud = 45
    quiet = 15
    evt_time = 0
    
    def _setup(self):
        pass
    
    def _start(self):
        self._generate_rhythm()
        self.evt_time = metronome.now()
        
    def _play(self):
        if random.randint(1,10) == 1:
            self._generate_rhythm()
        for length, short, loud in self.rhythm:
            length *= self.beat
            if short:
                dur = max(self.beat * .2, 0.1)
            else:
                dur = max(length * .8, 0.1)
            
            dur = length * 0.5
            if loud:
                velocity = self.loud
            else:
                velocity = self.quiet
            #print 'playing pitch',self.pitch
            self._out(self.pitch, dur, velocity, 1, 'rhythm')
            #print self.pitch, dur, velocity
            self.evt_time += length
            wait_until(self.evt_time)
        
    
    def _generate_rhythm(self):
        length = random.randint(4,8)
        rhythm = []
        for _ in range(length):
            dur = random.choice([1,2])
            short = random.choice([True, False])
            loud = random.choice([True, False])
            rhythm.append([dur, short, loud])
        self.rhythm = rhythm
        
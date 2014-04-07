import random
import global_vars
import time
from music.theory.map.data_map import DataMap
from music.theory.map.pitch_map import PitchMap
from utilities import (sprout, scale, scale_constrain, 
                       route, shift_scale, color)
from global_vars import events
from jazziness import Jazziness
from effects import Humanize, Echo, Gain

kinect = global_vars.kinect
midi = global_vars.midi
key = global_vars.key

beat = 0.125

crazychord = tuple([pitch+key for pitch in [-10, -3, 0, 5, 11, 16, 19]])

class Autonomous:
    playing = False
    pitches = None
    midi_out = None
    
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self._setup()
    
    def play(self):
        self._start()
        self.playing = True
        sprout(self._play_loop)
    
    def start(self):
        self.play()
    
    def _play_loop(self):
        while self.playing:
            self._play()
    
    def _start(self): pass #setup when playing starts
    def _play(self): pass
    def _setup(self): pass
    
    def stop(self):
        self.playing = False
        self._stop()
    
    def _stop(self):
        pass
    
    def note(self, pitch, dur, velocity, layer=0, keycode=None):
        self._out(pitch, dur, velocity, layer, keycode)
    
    def _out(self, pitch=60, dur=0.25, velocity=64, layer=0, keycode=None):
        """Target for sending notes out within the _in function"""
        if self.midi_out is None:
            self.midi_out = midi
            #print color('WARNING',"The midi out object is missing.  Defaulting to midi controller.")
        self.midi_out.note(pitch, dur, velocity, layer, keycode)

class TremoloTexture(Autonomous):
    key = 0
    def _setup(self):
        events.listen('facing_front', self.front_shift)
        events.listen('facing_back', self.back_shift)
    
    def _start(self):
        self.set_crazychord(crazychord)
    
    def _play(self):
        pitch = random.choice(crazychord) + random.randint(-1, 1) * 12
        velocity = 30
        dur = random.randint(5, 10) * .02
        
        self._out(pitch, dur, velocity, velocity)
        time.sleep(dur*.5)
    
    def front_shift(self):
        newkey = 0
        self.set_crazychord(shift_scale(crazychord, newkey))
        self.key = newkey
    
    def back_shift(self):
        newkey = random.choice((-6,-6,-4,-2))
        self.set_crazychord(shift_scale(crazychord, newkey))
        self.key = newkey
    
    def set_crazychord(self, chord):
        global crazychord
        for pitch in crazychord:
            midi.unlockPitch(pitch)
        for pitch in chord:
            midi.lockPitch(pitch, 'crazychord')
        crazychord = chord
        
class ChordHits(Autonomous):
    shortcount = 0
    
    def _start(self):
        sprout(kinect.calc_speed)
    
    def _play(self):
        global beat
        
        smallest_area = 10
        for dur, wait in random.choice([
                                        [(4,5), (1,4)], 
                                        [(2,2),(1,4),(2,3)],
                                        [(3,3),(1,1),(1,2),(1,2),(1,2)]
                                        ]):
            
            area = kinect.area
            
            if area > 0.5:
                velocity = int(scale_constrain(area, 0, 1, 10, 127))
                
                beat = max(min((30 - kinect.speed_ramp) / 120., 0.25), 0.03)
                if beat == 0.03:
                    self.shortcount += 1
                    if self.shortcount > 20:
                        events.send('stop_all_sections')
                else:
                    self.shortcount = 0
                for pitch in crazychord:
                    #self._out(pitch, dur*beat, velocity, 2)
                    self._out(pitch, dur*beat, velocity, 2, 'crazychord')
                time.sleep(wait * beat*1.)
            else:
                time.sleep(beat)


class Polycrystalline(Autonomous):
    pitch_map = None
    r = 0
    octave = 48
    time = 0
    increments = (-3,-1,2,4,-2)
    facing = True
    i = 0
    skip = 0
    dur = 0.3
    jazziness = None
    pitch_maps = None
    
    def __init__(self, octave=60):
        self.octave = octave
        self.time = time.time()        
        #self.pitch_map = PitchMap([x+octave for x in 2,9,12,17,23,28,31], variance=50)
        chords = (
              (-10,-3,0,5,11,16,19),
              (-17,-10,-3,12,17,23,26),
              (-15,-7,0,11,16,21,24),
              (-7,0,4,9,14,19,23)
              )
        
        self.pitch_maps = []
        for chord in chords:
            self.pitch_maps.append(PitchMap([x+octave for x in chord], variance=50))
        
        self.pitch_map = self.pitch_maps[0]
        self.rhythm = random.choice( ((1,1,2), (1,1,2,1,1,1,1,2)) )
        self.velocity_map = DataMap([random.randint(60, 127) for _ in range(7)], variance=50)
        self.jaggedness = 0.
        
        Autonomous.__init__(self)
        events.listen('facing_front', self.front_shift)
        events.listen('facing_back', self.back_shift)
    
    def front_shift(self):
        pass#self.pitch_map.setItems(self.front_chord)

    def back_shift(self):
        pass#self.pitch_map.setItems(self.back_chord)
            
    def _play(self):
        self.jazziness = Jazziness.retrieve()
        i = 0
        skip = False
        self.time = time.time()
        while self.playing:
            swing = self.jazziness.swing
            jaggedness = self.jazziness.jaggedness
            if jaggedness > .5:
                midi.setSustain(False)
            else:
                midi.setSustain(True)
            
            for beattype in 'long', 'short':
                pitch = self.pitch_map.pick()
                dur = self.dur
                if self.rhythm[self.i] == 1:
                    i+=1
                elif self.rhythm[self.i] == 2 and not skip:
                    skip = True
                elif skip:
                    skip = False
                    i += 1
                    if beattype == 'long':
                        dur *= swing
                    else:
                        dur *= (1-swing)
                    self.time += dur
                    time.sleep(self.time - time.time())
                    continue
                
                velocity = int(scale(self.velocity_map.pick(), 
                                     0, 127, 
                                     (1.-jaggedness)*.4*127, 127-(1.-jaggedness)*.6*127))
                self._out(pitch, 0.2, velocity, 1)
                self.skip = 0
                self.i = (self.i + 1) % len(self.rhythm)
                
                if beattype == 'long':
                    dur *= swing
                else:
                    dur *= (1-swing)
                self.time += dur
                time.sleep(self.time - time.time())
        

class HumanizedRepetition(Autonomous):
    humanize = None
    echo = None
    gain = None
    
    def __init__(self, humanize=None, echo=None, gain=None):
        if humanize is not None:
            self.humanize = humanize
        else:
            self.humanize = Humanize(delay_max = 0.01, velocity_max = 50)
        
        if echo is not None:
            self.echo = echo
        else:
            self.echo = Echo(decay=0.85, delay=0.2, decay_variability=0.1)
        
        if gain is not None:
            self.gain = gain
        else:
            self.gain = Gain()
            self.gain.fade(0,1,10)
        
        self.notes = (4,5,7,11,12)
        self.octaves = (2,3,4,6,7,8)
        
    
    def _play(self):
        midi.setSustain(True)
        
        route(self.echo, self.humanize)
        route(self.humanize, self.gain)
        route(self.gain, midi)
        
        note_choices = [x + octave*12 for x in (4,5,7,11,12) for octave in (1,2,3,4,5,6,7,8)]
        
        while self.playing:
            t = time.time()
            self.echo.note(random.choice(note_choices), 0.15,40)
            time.sleep(random.choice((0.2,0.4)) - time.time() + t)
    

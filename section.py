import random
import time
from autonomous import (TremoloTexture, ChordHits, 
                        Polycrystalline, HumanizedRepetition)
from instruments import Echo, Tremolo
from air_piano import AirPiano
from effects import Gain, Octaves
from utilities import route, sprout
from global_vars import midi, events
from music.theory.map.pitch_map import PitchMap
from americana import Americana, Rhythm

open_sections = []

class Section:
    """A structural section of the music.  
    
    This is where the composition happens."""
    
    playing = False
    solo = False #if True, kills all other sections when it starts
    
    def __init__(self, start_token=None, stop_token=None):
        if start_token is not None:
            events.listen(start_token, self.start)
        if stop_token is not None:
            events.listen(stop_token, self.stop)
        self._setup()
    
    def start(self):
        self.playing = True
        open_sections.append(self)
        self._start()
    
    def stop(self):
        self.playing = False
        if self in open_sections:
            open_sections.remove(self)
        self._stop()
    
    def toggle(self):
        if self.playing:
            self.stop()
        else:
            self.start()
    
    def _setup(self): pass
    def _start(self): pass
    def _stop(self): pass
    
    
    @staticmethod
    def stop_all():
        for section in open_sections:
            sprout(section.stop)
        events.disable()
        for pitch in [octave*12+p for p in (0,1,2,3,4,5,6,7,8,9,10,11) for octave in (0,1,2,3,4,5,6,7,8)]:
            midi.note(pitch, 5., 127, 5)
        midi.setSustain(False)
        print 'stopping'
        midi.silence = True
        
            
events.listen('stop_all_sections', Section.stop_all)

ap = AirPiano()
class AirPianoSection(Section):
    def _start(self):
        if not ap.playing:
            ap.run()
    
    def _stop(self):
        pass

class AirPiano2Section(Section):
    def _start(self):
        ap.change_pitches = True
        ap.set_hand_instrument('righthand', Echo, delay=0.25, decay=0.8, decay_variability=.15)
        #self.ap.set_hand_pitches('lefthand',[-3])
        if not ap.playing:
            ap.run()
    
    def _stop(self):
        ap.stop()

class HumanizedRepetitionSection(Section):
    def _setup(self):
        self.hr = HumanizedRepetition()
    
    def _start(self):
        self.hr.play()
    
    def _stop(self):
        if hasattr(self, 'hr'):
            self.hr.stop()
            #sprout(self._fade_out)
    
    #def _fade_out(self):
    #    self.hr.gain.fade(1., 0., 10)
    #    time.sleep(10)
    #    self.hr.stop()
        
class PolycrystallineSection(Section):
    prev_chord_index = -1
    def _setup(self):
        #events.listen('switch_top_lefthand', self.toggle)
        #events.listen('switch_left', self.left_hit)
        #events.listen('switch_right', self.right_hit)
        self.fader = Gain()
        self.polys = []
    
    def _start(self):
        self.fader.fade(0., 1., 15)
        self.octaves = Octaves(span=2)
        route(self.fader, self.octaves)
        route(self.octaves, midi)
        self.polys = []
        events.listen('facing_back', self.chord_change)
        events.listen('facing_front', self.chord_change)
        for _ in range(4):
            p = Polycrystalline(60)
            route(p, self.fader)
            self.polys.append(p)
            p.play()
        #sprout(self._chord_change)
    
    def _stop(self):
        sprout(self._fade_out)
        events.unlisten('facing_back', self.chord_change)
        events.unlisten('facing_front', self.chord_change)
    
    def _fade_out(self):
        self.fader.fade(1., 0., 10)
        time.sleep(10)
        for p in self.polys:
            p.stop()
    
    def chord_change(self):
        i = self.prev_chord_index
        while i ==self.prev_chord_index:
            i = random.choice(range(len(self.polys[0].pitch_maps)))
        
        for p in self.polys:
            p.pitch_map = p.pitch_maps[i]
        self.prev_chord_index = i

class AmericanaSection(Section):
    americana = None
    def _setup(self):
        self.americana = Americana()
    
    def _start(self):
        self.americana.play()
    
    def _stop(self):
        self.americana.stop()

class RhythmSection(Section):
    rhythms = None
    def _setup(self):
        self.fader = Gain()
        route(self.fader, midi)
        self.rhythms = []
    
    def _start(self):
        for pitch in 24,48,84,96:
            midi.lockPitch(pitch, 'rhythm')
            r = Rhythm(pitch=pitch, beat=0.125)
            r.loud = 50
            r.quiet = 20
            route(r, self.fader)
            self.rhythms.append(r)
    
        self.fader.fade(1.5, 1., 10)
        for r in self.rhythms:
            r.start()
    
    def _stop(self):
        for r in self.rhythms:
            r.stop()

class BeatSection(Section):
    polys = None
    fader = None
    def _setup(self):
        events.listen('facing_front', self.front_shift)
        events.listen('facing_back', self.back_shift)
        self.fader = Gain()
        self.fader.vel_multiplier = 0.5
        route(self.fader, midi)
    
    def _start(self):
        self.polys = []
        for _ in range(5):
            p = Polycrystalline(60)
            #p.front_chord = [-3+octave*12 for octave in 1,2,7,8]
            p.front_chord = [0+octave*12 for octave in 1,2,7,8]
            p.back_chord = [0+octave*12 for octave in 1,2,7,8]
            p.pitch_map = PitchMap(p.front_chord, variance=50)
            route(p,self.fader)
            self.polys.append(p)
            p.play()
    
    def _stop(self):
        sprout(self._fade_out)
        events.unlisten('facing_front', self.front_shift)
        events.unlisten('facing_back', self.back_shift)
    
    def _fade_out(self):
        self.fader.fade(1., 0., 10)
        time.sleep(10)
        for p in self.polys:
            p.stop()
    
    def front_shift(self):
        if type(self.polys) is list:
            front_chord = [random.choice((-3, -1, 2, 4, 7))+octave*12 for octave in 1,2,7,8]
            for p in self.polys:
                p.front_chord = front_chord

    def back_shift(self):
        if type(self.polys) is list:
            back_chord = [random.choice((-4, -2, 0, 1, 3))+octave*12 for octave in 1,2,7,8]
            for p in self.polys:
                p.back_chord = back_chord
            
class TopTremoloSection(Section):
    trem = None
    
    def _setup(self):
        events.listen('facing_front', self.front_shift)
        events.listen('facing_back', self.back_shift)
        self.front_pitches = [x+84 for x in 2,4,5,7,9,11,12,14]
        self.back_pitches = [x+84 for x in 1,3,5,7,8,10,12,13]
        self.trem = Tremolo(self.front_pitches, 30, crescendo=False)
    
    def front_shift(self):
        self.trem.pitches = self.front_pitches

    def back_shift(self):
        self.trem.pitches = self.back_pitches
    
    def _start(self):
        self.trem.start()
    
    def _stop(self):
        self.trem.stop()
        events.unlisten('facing_front', self.front_shift)
        events.unlisten('facing_back', self.back_shift)

class TremAndHitsSection(Section):
    kill = []
    def _start(self):
        #self.fader = Gain()
        #self.fader.fade(0, 1., 10)
        self.trem = TremoloTexture()
        #route(self.trem, self.fader)
        #route(self.fader, midi)
        for _ in xrange(2):
            self.trem.play()
        
        self.hits = ChordHits()
        self.hits.play()

    def _stop(self):
        self.hits.stop()
        self.trem.stop()
        self.fader.vel_multiplier = 0.
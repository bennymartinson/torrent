from music.midi import MidiPlayer
import time
from utilities import sprout, scale

mp_instance = None

class MidiInterface(MidiPlayer):
    beat = 0.1
    velocity_scale = (2, 127)
    _quantize = False
    _tasks = None
    _beat_registry = None
    _play_patterns = False
    pattern_period = 23
    sustain = False
    silence = False
    locked_pitches = None
    
    @staticmethod
    def retrieve(channel=1):
        """ Retrieves a singleton MidiInterface instance, and creates it if it doesn't exist. """
        global mp_instance
        if mp_instance is None:
            mp_instance = MidiInterface(channel)
        return mp_instance
    
    def __init__(self, channel=1):
        self._beat_registry = []
        self._tasks = []
        self.locked_pitches = {}
        MidiPlayer.__init__(self, channel)
        sprout(self._sustainLoop)
    
    def lockPitch(self, pitch, keycode):
        self.locked_pitches[pitch] = keycode
    
    def unlockPitch(self, pitch):
        if pitch in self.locked_pitches:
            del self.locked_pitches[pitch]
    
    def note(self, pitch=60, dur=1, velocity=80, layer=0, keycode=None, affect=True):
        if pitch in self.locked_pitches and keycode != self.locked_pitches[pitch]:
            #print 'restricted pitch',pitch
            return
        if self.silence: return
        if velocity <= 1 and type(velocity) is float:
            adjusted_velocity = int(round(scale(velocity, 0., 1., *self.velocity_scale)))
        else:
            adjusted_velocity = int(round(scale(velocity, 0, 127, *self.velocity_scale)))
        if self.sustain:
            dur = 0.1 # set duration to minimum, since pedal will be down anyway.
        
        if affect:
            self._addFunc(MidiPlayer.note, self, pitch, dur, adjusted_velocity, layer)
        else:
            MidiPlayer.note(self, pitch, dur, velocity, layer)
    
    def setSustain(self, sustain):
        self.sustain = sustain
    
    def _sustainLoop(self):
        while True:
            MidiPlayer.setSustain(self, self.sustain)
            time.sleep(1.)
    
    def start_quantize(self, beat):
        self.beat = beat
        self._quantize = True
        sprout(self._quantize_loop)
        
    def stop_quantize(self):
        self._quantize = False
        
    def _quantize_loop(self):
        while self._quantize or len(self._tasks):
            events = []
            for task in self._tasks:
                self._doFunc(*task)
                pitch = task[1][1]
                dur = task[1][2]
                velocity = task[1][3]
                events.append((pitch, dur, velocity))
            if self._play_patterns:
                self._beat_registry.append(events)
                self._detect_patterns()
            self._tasks = []
            time.sleep(self.beat)
    
    def _detect_patterns(self):
        if len(self._beat_registry) <= self.pattern_period:
            return;
        
        past_events = self._beat_registry[0]
        present_events = self._beat_registry[self.pattern_period]
        patterns = []
        self._beat_registry = self._beat_registry[-7:]
        
        for event1 in past_events:
            for event2 in present_events:
                if event1[0] == event2[0]: # if the 2 beats contain the same pitch
                    patterns.append((event1[0], (event1[1]+event2[1])/2, (event1[2]+event2[2])/2))
        
        for pattern in patterns:
            print "found a pattern:",pattern
            sprout(self._pattern_loop, pattern)
        
    def _pattern_loop(self, pattern):
        velocity = pattern[2]
        while self._play_patterns and velocity > 1:
            velocity *= 0.99
            time.sleep(self.beat*self.pattern_period)
            self.note(pattern[0], pattern[1], int(velocity), 0, False)
    
    def _addFunc(self, func, *args):
        if self._quantize:
            self._tasks.append((func, args))
        else:
            self._doFunc(func, args)
    
    def _doFunc(self, func, args):
        func(*args)
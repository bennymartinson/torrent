import random
from utilities import scale_constrain, sprout, wait_for
from instruments import Tremolo, Echo
import global_vars


kinect = global_vars.kinect

class AirPiano:
    """Class that uses kinect data to let the presenter play the "air piano" """
    octave_spacing = 210 # the x distance between 2 octaves, assuming comfy distance of 70 pt, w/ 3 notes per octave
    key = 0
    playing = False
    change_pitches = False
    
    hand_width = None
    hand_instruments = None
    
    def __init__(self):
        self.pitches = {'lefthand': [2, 4, 9, 12, 14, 16, 21, 24],
                        'righthand': [5, 11, 16, 19]}
        
        self.pitch_options = {'lefthand' : [[0,2,7],
                                            [-3,-1,4],
                                            [-7,-5,0]],
                              'righthand' : [[2,4,11],
                                             [5,7,12],
                                             [7,9,14]]}
        
        self.hand_width = {'lefthand': 210, 
                           'righthand': 0}
        
        self.hand_instruments = {'lefthand': (Tremolo, {}),
                                 'righthand': (Echo, {'delay':0.5, 'decay':0.8, 'decay_variability':.1})}
    
    def set_hand_instrument(self, hand, instrument, **kwargs):
        self.hand_instruments[hand] = (instrument, kwargs)
        
    def set_hand_pitches(self, hand, pitches):
        self.pitches[hand] = pitches
    
    def run(self):
        sprout(kinect.calc_speed)
        self.playing = True
        for hand in 'lefthand', 'righthand':
            sprout(self._run_hand, hand)
    
    def stop(self):
        self.playing = False
        kinect.calculating_speed = False
    
    def _calc_velocity(self, hand, slide=False):
        if slide:
            velocity = int(scale_constrain(kinect.speed_piano[hand][global_vars.X], 
                                       0, 150, 10, 100))
        else:
            velocity = int(scale_constrain(kinect.speed_piano[hand][global_vars.Y], 
                                       0, 150, 10, 127))
        return velocity
    
    def _get_pitch_indices(self, hand, x1, x2):
        note_spacing = self.octave_spacing / len(self.pitches[hand])
        index1 = int(scale_constrain(x1, -700, 700, 0, 1400 / note_spacing))
        index2 = int(scale_constrain(x2, -700, 700, 0, 1400 / note_spacing))
        return range(index1, index2+1)
    
    def _get_pitch(self, index, hand):
        note_spacing = self.octave_spacing / len(self.pitches[hand])
        middle = 700 / note_spacing
        dist_from_middle = index - middle
        # let's put the note closest to middle C (60) in the middle of the keyboard
        pc = self.pitches[hand][dist_from_middle % len(self.pitches[hand])]
        octave = int(dist_from_middle / len(self.pitches[hand])) + 5 # ( 5 is 60 % 12 )
        return pc + 12 * octave + self.key
    
    def _hand_pitches(self, x, hand):
        width = self.hand_width[hand]
        pitch_indices = self._get_pitch_indices(hand, x-width/2, x+width/2)
        return [self._get_pitch(index, hand) for index in pitch_indices]
    
    def _change_pitches(self, hand):
        if self.change_pitches:
            self.set_hand_pitches(hand, random.choice(self.pitch_options[hand]))
    
    def _run_hand(self, hand):
        instrument = None
        while self.playing:
            inst_class, inst_kwargs = self.hand_instruments[hand]
            
            self._change_pitches(hand)
            
            x = wait_for(kinect.hand_hit, (hand,))
            if not self.playing: #we waited a while, so have to check again
                return
            hit_location = x
            pitches = self._hand_pitches(x, hand)
            velocity = self._calc_velocity(hand, slide=False)
            
            if instrument is not None:
                instrument.stop()
            
            instrument = inst_class(pitches, velocity, **inst_kwargs)
            instrument.start()
            
            while(x):
                new_pitches = self._hand_pitches(x, hand)
                if new_pitches != pitches:
                    pitches = new_pitches
                    velocity = self._calc_velocity(hand, slide=True)
                    instrument = instrument.slide(pitches, velocity)
                x = kinect.hand_slide(hand, hit_location)
                hit_location = None 
            instrument.stop()

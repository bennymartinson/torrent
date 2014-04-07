from pitch_class_structure import PitchClassStructure
import pitch

''' A type of pitch class structure, defined by mode and a root. '''

class Scale(PitchClassStructure):
    mode = 'ionian'
    
    def __init__(self, root=0, mode='ionian'):
        self.root = root
        self.set_mode(mode)
        self.clean()
    
    def get_tone(self, tone, octave=0):
        if type(tone) is str:
            tone = tones[tone]
        ret = self.pitches[tone]
        if ret < self.root:
            ret += 12
        return ret+pitch.octaves(octave)
    
    def set_mode(self, mode):
        self.mode = mode
        self.pitches = [x + self.root for x in modes[mode]]
    
    def sort(self): #override sorting to preserve structure order over pitch class ordinality
        ret = sorted([pitch.pc(x - self.root) for x in self.pitches])
        ret = [pitch.pc(x + self.root) for x in ret]
        self.pitches = ret
        return self
    

modes = { 'ionian':[0,2,4,5,7,9,11], 'dorian':[0,2,3,5,7,9,10], 'phrygian':[0,1,3,5,7,8,10],
          'lydian':[0,2,4,6,7,9,11], 'mixolydian':[0,2,4,5,7,9,10], 'aeolian':[0,2,3,5,7,8,10],
          'locrian':[0,1,3,5,6,8,10],
          'j_ionian':[0,2,3,5,7,9,11], 'j_dorian':[0,1,3,5,7,9,10], 'j_phrygian':[0,2,4,6,8,9,11],
          'j_lydian':[0,2,4,6,7,9,10], 'j_mixolydian':[0,2,4,5,7,8,10], 'j_aeolian':[0,2,3,5,6,8,10],
          'j_locrian':[0,1,3,4,6,8,10]}
          
tones = { 'root':0, 'second':1, 'third':2, 'fourth':3, 'fifth':4, 'sixth':5, 'seventh':6 }

if (__name__ == '__main__'):
    sc = Scale(2, 'dorian')
    print sc.pitches
    print sc.get_tone('third')
from pitch_class_structure import PitchClassStructure
from pitch import *
from music.theory.pitch.pitch import interval_to_tone

qualities = { 'major':[0,4,7], 'maj7':[0,4,7,11], 'maj6':[0,4,7,9],
              'minor':[0,3,7], 'min7':[0,3,7,10], 'min6':[0,3,7,9], 'min9':[0,3,7,10,14],
              'dom7':[0,4,7,10], 'iiOverDom':[0,2,7,10], 'dim7':[0,3,6,9] }

class Chord(PitchClassStructure):
    """A type of pitch class structure, defined by quality and a root."""
    quality = 'major'
    
    tone_precedence = ['root', 'third', 'seventh', 'second', 'fifth', 'sixth']
    
    def __init__(self, root=0, quality='major'):
        self.quality = quality
        self.pitches = qualities[quality]
        self.transpose(root)
        self.clean()
        
    def print_out(self):
        print "root:", self.root, "| quality:", self.quality, "| pitches:", self.pitches
        return self
    
    @staticmethod
    def get_quality(pitches):
        try:
            return (key for key,value in qualities.items() if value==pitches).next()
        except StopIteration:
            return False

if (__name__ == '__main__'):
    ch = Chord(1, 'dom7')
    print ch.pc_precedence()
    ch.print_out()
    print Chord.get_quality([0,3,7])
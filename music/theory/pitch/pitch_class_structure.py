''' a pitch class set with some sort of organization of pitches, such as a scale, chord, or other shape '''
from pitch_class_set import PitchClassSet
import pitch

class PitchClassStructure(PitchClassSet):
    root = 0
    tone_precedence = ["root"]
    
    def transpose(self, amt):
        self.root = self.root + amt
        return PitchClassSet.transpose(self, amt)
    
    def pitch_to_tone(self, pitch):
        return pitch.name_tone(pitch.interval_to_tone(pitch - self.root))
    
    def tone_to_pitch(self, tone):
        intervals = pitch.tone_to_intervals(tone)
        pitches = [pitch.pc(i+self.root) for i in intervals]
        for p in self.pitches:
            if p in pitches:
                return p
        return None

    def pc_precedence(self):
        pcp = [self.tone_to_pitch(tone) for tone in self.tone_precedence]
        pcp = filter(lambda x: x is not None, pcp)
        pcp_length = len(pcp)
        return {pcp[i]:pcp_length-i for i in range(pcp_length)}
        
    ### Cleaning operations
    def clean(self):
        self.root = pitch.pc(self.root)
        PitchClassSet.clean(self)
        
    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)
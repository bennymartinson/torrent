from pitch_set import PitchSet
from pitch import *
from copy import copy

''' An unordered group of unique pitch classes'''

class PitchClassSet(PitchSet):
    range = 21, 108 # this is the MIDI range of a piano 
    
    def get_chord(self):
        iset = self.getIntervalSet()
        qualityandinversion = iset.is_chord()
        if (qualityandinversion):
            import chord
            quality = qualityandinversion[0]
            pitch = self.pitches[qualityandinversion[1]]
            return chord.Chord(pitch, quality)
        else:
            return False
    
    def closest_pitch(self, pitch, index=0):
        p = [octavize(i, pitch) for i in self.pitches]
        if octavize(pitch-6, pitch) in p:
            p.append(pitch+6)
        
        p.sort(key=lambda i: min_tone_distance(pitch, i))
        return p[min([index,len(p)])]
    
    def voice_lead(self, pitch_set):
        pcopy = copy(pitch_set.pitches)
        ret = []
        while len(pcopy):
            p = pcopy[0]
            del pcopy[0]
            ret.append(self.closest_pitch(p, [x % 12 for x in pcopy].count(p % 12)))
            
        def not_too_low(pitch):
            if (pitch < 48):
                pitch = octavize(pitch, 48)
            return pitch
        
        ret = [not_too_low(pitch) for pitch in ret]
        return PitchSet(*ret)
    
    def get_all(self):
        ret = []
        lowest, highest = self.range
        for p in self.pitches:
            p = pc(p)
            while p < 128:
                if p >= lowest:
                    ret.append(p)
                if p > highest:
                    break;
                p += 12
        ret.sort()
        return ret
    
    ### Cleaning operations
    def clean(self):
        self.pc().uniquize()
        PitchSet.clean(self)
        
    def pc(self):
        self.pitches = map(pc, self.pitches)
        return self

if (__name__ == '__main__'):
    pcs = PitchClassSet(0,4,7).transpose(67)
    
    ps = PitchSet(60, 67, 76)
    pcs.voice_lead(ps).print_out()
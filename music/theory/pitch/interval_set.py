from pitch_class_set import PitchClassSet
import copy

''' an unordered set of intervals above a single pitch '''

class IntervalSet(PitchClassSet):
    def is_chord(self):
        import chord
        c = copy.copy(self)
        for inversion in range(0, len(self.pitches)):
            quality = chord.Chord.get_quality(c.pitches)
            if quality:
                return quality, inversion
            c.inversion()
        return False
    
    ### Cleaning operations
    def clean(self):
        self.normalize()
        PitchClassSet.clean(self)
        
    def normalize(self):
        def subtractAmt(x): return x - min(*self.pitches)
        self.pitches = map(subtractAmt, self.pitches)
        return self
        
if (__name__ == '__main__'):
    iset = IntervalSet(0,5,8)
    iset.print_out()
    ch = iset.is_chord()
    print ch
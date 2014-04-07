''' An unordered group of non-unique pitches'''

class PitchSet:
    pitches = []
    
    def __init__(self, *pitches):
        self.pitches = list(pitches)
        self.clean()
    
    def transpose(self, amt):
        def addAmt(x): return x + amt
        self.pitches = map(addAmt, self.pitches)
        
        self.clean()
        return self
        
    def print_out(self):
        print self.pitches
    
    def inversion(self, times=1, firstCall=True):
        if (times == 0):
            pass
        elif (times > 0):
            self.inversion(times - 1, False)
            if (firstCall):
                self.sort()
            p = self.pitches.pop(0)
            self.pitches.append(p+12)
        elif (times < 0):
            self.inversion(times + 1, False)
            if (firstCall):
                self.sort()
            p = self.pitches.pop()
            self.pitches.insert(0, p-12)
        
        self.clean()
        return self
    
    def addPitches(self, *pitches): 
        self.pitches.extend(pitches)
        self.clean()
        return self
    
    def getPitchSet(self):
        return PitchSet(*self.pitches)
    
    def getPitchClassSet(self):
        from pitch_class_set import PitchClassSet
        return PitchClassSet(*self.pitches)
        
    def getIntervalSet(self):
        from interval_set import IntervalSet
        return IntervalSet(*self.pitches)
    
    def getChord(self):
        pcs = self.getPitchClassSet()
        return pcs.getChord()
    
    def union(self, ps2):
        self.addPitches(*ps2.pitches)
        #addPitches does the cleaning
        return self
    
    ### Cleaning operations
    def clean(self):
        self.sort()
    
    def uniquize(self):
       self.pitches = list(set(self.pitches))
       return self
    
    def sort(self):
        self.pitches.sort()
        return self

      
if (__name__ == "__main__"):
    PitchSet(60, 69, 77).getChord().print_out()
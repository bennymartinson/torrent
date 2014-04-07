import copy

class Rhythm:
    vals = []
    denom = 1
    cursor = 0
    next = 0
    repeatNum = 1
    
    def __init__(self, *args):
        self.vals = args
    
    def getDuration(self):
        rhythm = copy.copy(self)
        sum = 0
        while (rhythm.getNext()):
            sum += rhythm.next['wait']
        return sum
        
    def setDenom(self, denom):
        self.denom = denom
        return self
        
    def setRepeat(self, num):
        self.repeatNum = num
        return self
        
    def getNext(self):
        if (self.cursor >= (self.repeatNum * len(self.vals))):
            return False
        
        cursor = self.cursor % len(self.vals)
        val = self.vals[cursor]
        if (type(val) is tuple):
            dur = val[0] * self.denom if (val[1] == 'long') else self.denom / 2.
            waitTime = val[0] * self.denom
        else:
            dur = self.denom / 2.
            waitTime = val * self.denom
        
        self.cursor += 1
        self.next = {'dur':dur, 'wait':waitTime}
        return self.next
    
    def reset(self):
        self.cursor = 0
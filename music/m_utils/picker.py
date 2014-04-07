import random

class Pick:
    pickings = []
    type = 'random'
    args = {}
    
    bucket = []
    
    def __init__(self, pickings, type='random', **args):
        self.pickings = pickings
        self.type = type
        self.args = args
        
    def pick(self):
        pickingsLength = len(self.pickings)
        if (self.type == 'random'):
            randindex = random.randint(0, pickingsLength-1)
            return self.pickings[randindex]
        elif (self.type == 'serial'):
            if (len(self.bucket) == pickingsLength):
                self.bucket = []
            def notInBucket(x):
                return (x not in self.bucket)
            remainingOptions = filter(notInBucket, self.pickings)
            if (len(remainingOptions) == 1):
                choice = remainingOptions[0]
            else:
                choice = remainingOptions[random.randint(0,len(remainingOptions)-1)]
            self.bucket.append(choice)
            return choice
            
p = Pick([0, 1, 2, 3], 'serial')
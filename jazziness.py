import time
from gesture import Smoothness
from utilities import sprout, scale_constrain
from global_vars import midi

jazziness_instance = None

class Jazziness:
    calculate = False
    swing = 0.5
    jaggedness = 0.
    snapshots = [0]
    sustain = False
    
    @staticmethod
    def retrieve():
        """ Retrieves a singleton instance, and creates it if it doesn't exist. """
        global jazziness_instance
        if jazziness_instance is None:
            jazziness_instance = Jazziness()
        return jazziness_instance
    
    def __init__(self):
        self.calculate = True
        sprout(self._calculate)
    
    def stop(self):
        self.calculate = False
    
    def _calculate(self):
        smoothness = Smoothness.retrieve()
        while self.calculate:
            lh = smoothness.value('lefthand')
            rh = smoothness.value('righthand')
            
            self.swing = round(scale_constrain(lh, 0, 150, 0.5, 0.7) * 100) * 0.01
            self.jaggedness = scale_constrain(rh, 0, 150, 0., 1.)
            self.snapshots.append((lh+rh)*.5)
            self.snapshots = self.snapshots[-5:]
            
            if self.snapshots[0] <= .5 and self.snapshots[-1] > .5:
                midi.setSustain(False)
            elif self.snapshots[0] >= .5 and self.snapshots[-1] < .5:
                midi.setSustain(True)
            time.sleep(0.1)
    
    
import meter
from music.theory.pitch import harmony

class Measure:
    meter = meter.Meter(4, 4)
    duration = 1
    
    def __init__(self, meter=None):
        if meter is not None:
            self.meter = meter
            self.clean()
    
    def clean(self):
        self.duration = self.meter.duration()
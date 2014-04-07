
class Tempo:
    quarter_dur = 1
    bpm = 60
    beat_unit = 1/4.
    
    def __init__(self, bpm = 60, beat_unit = 1/4.):
        self.bpm = bpm
        self.beat_unit = beat_unit
        self.clean()
        
    def clean(self):
        self.quarter_dur = 60. / (self.bpm * self.beat_unit * 4)
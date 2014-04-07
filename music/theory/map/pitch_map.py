from number_map import NumberMap
from music.theory.pitch.pitch import pc

class PitchMap(NumberMap):
    prevMap = None
    
    def adjust_for_voice_leading(self, weights):
        '''works similarly to linearity, except considers all past choices equally'''
        
        return weights


if __name__ == '__main__':
    pm = PitchMap(range(60, 82), variance=200, gravity=5)
    print pm.select(10)
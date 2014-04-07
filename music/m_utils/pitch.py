import math

def mtof(midi):
    return 2. ** ((midi-69) / 12.)*440
    
def ftom(freq):
    return 12 * math.log((freq/440.), 2)+69
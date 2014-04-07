'''definitions and functions for pitches, intervals, and tones, all of which are just represented as integers'''


pitches = { 'C':0, 'C#':1, 'Db':1, 'D':2, 'D#':3, 'Eb':3, 'E':4, 'F':5, 'F#':6,
            'Gb':6, 'G':7, 'G#':8, 'Ab':8, 'A':9, 'A#':10, 'Bb':10, 'B':11 }
           
intervals = { 'unis':0, 'root':0, 'm2':1, 'M2':2, 'm3':3, 'M3':4, 'P4':5, 
              'tt':6, 'P5':7, 'm6':8, 'M6':9, 'm7':10, 'M7':11 }
              
tones = [[0], [1,2], [3,4], [5,6], [7], [8,9], [10,11]]

tone_names = ['root', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh']

roman_numerals = {'i':0, 'bii':1, 'ii':2, 'biii':3, 'iii':4,'iv':5, 
                  'bv':6, 'v':7, 'bvi':8, 'vi':9, 'bvii':10, 'vii':11}


def music_mod(tone, mod=12):
    ret = tone % mod
    if (ret < 0): return ret + mod
    else: return ret

def pc(pitch):
    return music_mod(pitch, 12)
    
def min_pc_distance(pitch1, pitch2):
    return min(music_mod(pitch1-pitch2, 12), music_mod(pitch2-pitch1, 12))
    
def min_tone_distance(pitch1, pitch2, scale_size=7):
    return min(music_mod(interval_to_tone(pitch1-pitch2), scale_size), music_mod(interval_to_tone(pitch2-pitch1), scale_size))

def interval_to_tone(interval):
    interval = pc(interval)
    for i in range(len(tones)):
        if (interval in tones[i]):
            return i
    return None

def tone_to_intervals(tone):
    tone_val = tone_names.index(tone)
    return tones[tone_val]

def name_tone(tone):
    if tone >= len(tone_names):
        return None
    return tone_names[tone]

def roman_numeral(numeral, key=0):
    return roman_numerals[numeral]+key

def octaves(num):
    return num * 12
    
def octavize(pitch, to_pitch):
    pitch = pc(pitch)
    to_pitch_octaves = int(to_pitch) / 12
    to_pitch = pc(to_pitch)
    if pitch > to_pitch:
        if pitch - to_pitch > 6:
            to_pitch_octaves -= 1
    else:
        if to_pitch - pitch > 6:
            to_pitch_octaves += 1
    return pitch + to_pitch_octaves * 12
    
def put_below(pitch, below_pitch):
    pitch = octavize(pitch, below_pitch)
    if (pitch <= below_pitch):
        return pitch
    else:
        return pitch - 12
        
def put_above(pitch, below_pitch):
    pitch = octavize(pitch, below_pitch)
    if (pitch >= below_pitch):
        return pitch
    else:
        return pitch + 12
        
if (__name__ == '__main__'):
    print tone_to_intervals('third')
    print min_tone_distance(71, 64)
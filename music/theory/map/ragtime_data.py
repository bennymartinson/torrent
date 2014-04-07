from music.theory.pitch.chord import Chord
from music.theory.pitch.pitch import roman_numeral
import music.theory.map.weights as w 

chord_leads = {}
chord_beats = {}
chord_durs = {}

default_qualities = {
    'i':'major', 'bii':'major','ii':'minor', 'biii':'major', 
    'iii':'minor', 'iv':'major', 'bv':'dim7', 'v':'dom7', 
    'bvi':'major', 'vi':'minor', 'bvii':'major', 'vii':'dim'
}

def register_chords(chords):
    beat = 0
    prev_chord = None
    for ch in chords:
        chord = None
        root = roman_numeral(ch[1],0)
        if len(ch) == 3:
            chord = (root, ch[2]) #use tuple as key...cool!
        else:
            chord = (root, default_qualities[ch[1]])
        
        register_association(chord_beats, beat, chord)
        register_association(chord_leads, prev_chord, chord)
        register_association(chord_durs, (beat, chord), ch[0])
        
        beat += ch[0]
        prev_chord = chord

def register_association(dic, item1, item2):
    if item1 in dic:
        if item2 in dic[item1]:
            dic[item1][item2] += 1
        else:
            dic[item1][item2] = 1
    else:
        dic[item1] = {item2: 1}

def generate_progression():
    prev_chord = None
    beat = 0
    choices = []
    while beat < 64:
        lead_weights = chord_leads[prev_chord]
        beat_weights = chord_beats[beat]
        weights = w.apply(lead_weights, beat_weights)
        weights = w.probabilitize(w.exp(weights, .5))
        choice = w.choose(weights)
        prev_chord = choice
        dur_weights = chord_durs[(beat, choice)]
        dur = w.choose(w.probabilitize(dur_weights))
        beat += dur
        choices.append((dur, choice))
    return choices

# maple leaf rag section A
register_chords([#
   [4, 'i'], [4, 'v'], [4, 'i'], [4, 'v'], 
   [2, 'bvi'], [2, 'v'], [2, 'bvi'], [2, 'v'], [8, 'i', 'minor'],
   [4, 'i', 'dim7'], [4, 'i'], [2, 'bvi'], [3, 'i'], [1, 'v'], [2, 'i'],
   [4, 'i', 'dim7'], [4, 'i'], [2, 'bvi'], [3, 'i'], [1, 'v'], [2, 'i']])

# maple leaf rag section B
register_chords([
   [8, 'v'], [8, 'i'], 
   [8, 'v'], [8, 'i'],
   [8, 'v'], [8, 'i'], 
   [4, 'vi', 'major'], [4, 'ii'],  [2, 'ii', 'dom7'], [2, 'v'], [4, 'i']])

# maple leaf rag section C
register_chords([
   [8, 'v'], [8, 'i'],
   [8, 'v'], [7, 'i'], [1, 'iii', 'dom7'],
   [8, 'vi', 'major'], [8, 'ii'],
   [4, 'i', 'dim7'], [2, 'i'], [2, 'vi', 'dom7'], [2, 'ii', 'dom7'], [2, 'v'], [4, 'i']])

# maple leaf rag section D
register_chords([
   [8, 'iv'], [8, 'i'],
   [8, 'v'], [8, 'i'],
   [8, 'iv'], [8, 'i'],
   [2, 'iv'], [2, 'ii', 'dom7'], [4, 'i'], [2, 'ii', 'dom7'], [2, 'v'], [4, 'i']])


# the fa'v'or'i'te section A
register_chords([
   [4, 'i'], [4, 'v'], [4, 'i'], [4, 'v'],
   [2, 'i', 'dim7'], [2, 'i'], [2, 'i', 'dim7'], [2, 'i'], [4, 'v'], [4, 'i'],
   [4, 'i'], [4, 'v'], [4, 'i'], [4, 'v'],
   [2, 'i', 'dim7'], [2, 'i'], [2, 'i', 'dim7'], [2, 'i'], [4, 'v'], [4, 'i']])

# the sycamore section B
register_chords([
   [8, 'v'], [8, 'i'], 
   [8, 'v'], [2, 'i'], [2, 'vi', 'dom7'], [4, 'ii'],
   [4, 'i', 'dim7'], [4, 'i'], [4, 'v'], [4, 'i']])

# the sycamore section C
register_chords([
   [4, 'i'], [4, 'i', 'dom7'], [2, 'iv'], [2, 'iv', 'minor'], [2, 'i'], [2, 'v'],
   [2, 'i'], [2, 'v', 'dim7'], [4, 'v', 'major'], [4, 'ii', 'dom7'], [4, 'v'],
   [4, 'i'], [4, 'i', 'dom7'], [2, 'iv'], [2, 'iv', 'minor'], [3, 'i'], [1, 'bvi', 'dim7'], 
   [2, 'vi'], [2, 'i'], [2, 'vi'], [2, 'i'], [2, 'i'], [2, 'v'], [4, 'i']])
   
# the cascades section A
register_chords([
   [4, 'i'], [4, 'v'], [4, 'i'], [4, 'v'],
   [2, 'bvi', 'dim7'], [2, 'vi'], [2, 'bvi', 'dim7'], [2, 'vi'], [8, 'i', 'dim7'], 
   [4, 'bvi', 'dom7'], [4, 'i'], [2, 'ii', 'dom7'], [2, 'v'], [4, 'i'],
   [4, 'bvi', 'dom7'], [4, 'i'], [2, 'ii', 'dom7'], [2, 'v'], [4, 'i']])

# the cascades section B
register_chords([
   [4, 'v'], [4, 'i'], [4, 'v'], [4, 'i'],
   [4, 'v'], [3, 'i'], [1, 'v', 'dom7'], [2, 'v', 'major'], [2, 'ii', 'dom7'], [4, 'v', 'major'],
   [4, 'v'], [4, 'i'], [4, 'v'], [4, 'i'], 
   [4, 'i', 'dom7'], [2, 'iv'], [2, 'vi', 'dom7'], [2, 'i'], [1, 'ii', 'dom7'], [1, 'v'], [4, 'i']])
        
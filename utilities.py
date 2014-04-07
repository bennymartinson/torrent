import time
import threading
import warnings

def sprout(function, *args):
    t = threading.Thread(target=function, args=args)
    t.daemon = True
    t.start()
    return t

def wait_for(function, args=()):
    while True:
        val = function(*args)
        if val:
            return val
        time.sleep(0.01)
        
def wait_until(dest_time):
    time.sleep(max(0, dest_time - time.time()))
    
def constrain(variable, minval, maxval):
    return max(min(variable, maxval), minval)

def scale(variable, fromlow, fromhigh, tolow, tohigh):
    amt = (variable - fromlow) / float(fromhigh-fromlow)
    return tolow + amt*(tohigh - tolow)

def scale_constrain(variable, fromlow, fromhigh, tolow, tohigh):
    variable = scale(variable, fromlow, fromhigh, tolow, tohigh)
    return constrain(variable, tolow, tohigh)

def stay_alive():
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print color('FAIL', 'keyboard exit')
        import os
        os.abort()
        
def route(from_obj, to_obj):
    if getattr(to_obj, 'midi_out', None) == from_obj:
        warnings.warn("The target is routed to the subject. This will create a feedback loop!")
    from_obj.midi_out = to_obj


scalenotes = [0,2,4,5,7,9,11]
def tonal_transpose(pitches, amt, root=0):
    ret = []
    
    key = calculate_key(pitches)
    if key is not False:
        root = key
    
    for pitch in pitches:
        pitch -= root
        octave = pitch / 12
        pc = pitch % 12
        if pc not in scalenotes:
            warnings.warn('Trying to transpose a note not in the scale!')
            ret.append(pitch+root)
            continue
        index = scalenotes.index(pc)
        index += amt
        octave += index / len(scalenotes)
        index = index % len(scalenotes)
        ret.append(scalenotes[index] + octave*12 + root)
    return ret

def shift_scale(pitches, newroot=-4, root=0):
    ret = []
    
    key = calculate_key(pitches)
    if key is not False:
        root = key
    
    newscale = [(pitch + newroot - root) % 12 for pitch in scalenotes]
    newscale.sort()
    
    for pitch in pitches:
        pitch -= root
        octave = pitch / 12
        pc = pitch % 12
        if pc not in scalenotes:
            warnings.warn('Trying to transpose a note not in the scale!')
            ret.append(pitch+root)
            continue
        index = scalenotes.index(pc)
        
        ret.append(newscale[index]+octave*12 + root)
    
    return ret

def calculate_key(pitches):
    pitches = [pitch % 12 for pitch in pitches]
    pitches = list(set(pitches))
    pitches.sort()
    if len(pitches) < 7:
        return False
    
    for i in range(12):
        p = [(pitch-i) % 12 for pitch in pitches]
        p.sort()
        
        if p == scalenotes:
            return i
    return False

def color(code, text):
    colors = {'HEADER': '\033[95m',
          'OKBLUE': '\033[94m',
          'OKGREEN': '\033[92m',
          'WARNING': '\033[93m',
          'FAIL': '\033[91m'}
    ENDC = '\033[0m'
    return colors[code]+text+ENDC

if __name__ == '__main__':
    print calculate_key((1,3,5,6,8,10,12))
    
    print tonal_transpose([0,4,7], -2)
    
    print shift_scale([0,2,4,5,7], 1)
        
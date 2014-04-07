from number_map import NumberMap
from music.theory.pitch.chord import Chord
import music.theory.pitch.pitch as pitch
import weights as w

class HarmonyMap(NumberMap):
    uniqueness = 0 # > 0, more unique than random, < 0, less than random
    precedence = 0 # > 0, enforce chord precedence, < 0, de-enforce
    spacing = 0 # > 1, enforce strong pitch spacing
    register = 0 # > 1, enforce a specific register
    register_center = 60
    precedences = None
    
    def __init__(self, items = {}, **kwargs):
        if isinstance(items, Chord):
            self.precedences = items.pc_precedence()
            items = items.get_all()
        super(HarmonyMap, self).__init__(items, **kwargs)
    
    def set_items(self, items):
        if isinstance(items, Chord):
            self.precedences = items.pc_precedence()
            items = items.get_all()
        if items is None:
            raise Exception('items was None!')
        self.setItems(items)
    
    def adjust(self, method="pick"):
        weights = super(HarmonyMap, self).adjust(method)
        weights = self.adjust_for_uniqueness(weights)
        if self.precedence != 0:
            weights = self.adjust_for_precedence(weights)
        if self.spacing != 0:
            weights = self.adjust_for_spacing(weights)
        if self.register != 0:
            weights = self.adjust_for_register(weights)
        return weights
    
    def adjust_for_uniqueness(self, weights):
        for k, v in weights.items():
            if k in self.prev_picks:
                weights[k] = v * pow(2., - self.uniqueness)
        return w.ensure_safe(weights)
    
    def adjust_for_precedence(self, weights):
        prec = {pitch.pc(p):w for p,w in self.precedences.items()}
        
        for k in weights.keys():
            if k not in prec:
                prec[k] = 1
        
        for p in self.prev_picks:
            pcp = pitch.pc(p)
            if pcp in prec:
                prec[pcp] *= 0.5
        
        mult = {k: prec[pitch.pc(k)] for k in weights.keys()}
        mult = w.scale(mult, float(self.precedence) / self.left_to_select)
        return w.normalize(w.apply(mult, weights))
    
    def adjust_for_spacing(self, weights):
        new_map = {k:1 for k in weights.keys()}
        for prev in self.prev_picks:
            octave = max(0, prev - 36) / 12
            too_close = 0
            if octave == 0:
                too_close = 11
            elif octave == 1:
                too_close = 4
            elif octave == 2:
                too_close = 2
            for k in weights.keys():
                if abs(prev - k) <= too_close:
                    new_map[k] *= pow(0.5, self.spacing)
        weights = w.apply(new_map, weights)
        return w.ensure_safe(weights)
    
    def adjust_for_register(self, weights):
        new_map = {}
        for k in weights.keys():
            distance = abs(self.register_center-k)+1
            new_map[k] = pow(distance, - self.register)
        weights = w.apply(new_map, weights)
        return w.ensure_safe(weights)


if __name__ == '__main__':
    hm = HarmonyMap(Chord(0, 'dom7'), uniqueness=10, precedence=10, spacing=2, register=10)
    print hm.precedences
    hs = hm.select(5)
    hs.sort()
    print hs
    print [pitch.pc(p) for p in hs]
    #print hm.adjust()
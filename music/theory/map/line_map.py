from number_map import NumberMap
import weights as w

class LineMap(NumberMap):
    linearity = 0 # > 0: next choice pulled toward prev, < 0: pushed away
    current_harmony = None
    directionality = 1 # > 0: enforce sense of direction to line
    noterange = 48,84
    
    def __init__(self, items = {}, **kwargs):
        if items == {} or items is None:
            items = {x:1 for x in xrange(21, 108)}
        super(LineMap, self).__init__(items, **kwargs)
    
    def adjust(self, method="pick"):
        weights = super(LineMap, self).adjust(method)
        if range is not None:
            weights = self.adjust_for_range(weights)
        if method == "pick":
            if self.linearity != 0:
                weights = self.adjust_for_linearity(weights)
        if self.current_harmony is not None:
            weights = self.adjust_for_current_harmony(weights)
        #if self.directionality != 0:
        #    weights = self.adjust_for_directionality(weights)
        return weights
        
    def adjust_for_current_harmony(self, weights):
        h = self.get_current_harmony()
        if h is None:
            return weights
        weights = w.multiply(weights, h.adjust())
        return weights
    
    def get_current_harmony(self):
        return self.current_harmony
    
    def adjust_for_linearity(self, weights):
        new_map = {}
        for k in weights.keys():
            if len(self.prev_picks) == 0:
                distance = 0
            else:
                distance = abs(k - self.prev_picks[-1])
            new_map[k] = pow(2, (- self.linearity * distance))
        
        weights = w.apply(new_map, weights)
        return w.ensure_safe(weights)
    
    def adjust_for_directionality(self, weights):
        _PAST_NOTES_TO_COUNT = 6
        new_map = {}
        direction_count = {'down':0, 'same':0, 'up':0}
        lpp = len(self.prev_picks)
        if lpp == 0:
            return weights
        for i in range(0,min(_PAST_NOTES_TO_COUNT, lpp-1)):
            picks = self.prev_picks[lpp-i-2:lpp-i]
            if picks[1] < picks[0]:
                direction_count['down'] += 1
            elif picks[1] > picks[0]:
                direction_count['up'] += 1
            else:
                direction_count['same'] += 1
        direction_difference = direction_count['up'] - direction_count['down']
        score = _PAST_NOTES_TO_COUNT - abs(direction_difference) + 1
        sign = lambda x,y: x < y
        if direction_difference < 0:
            sign = lambda x,y: x > y
        for k in weights.keys():
            prev_pick = self.prev_picks[-1:][0]
            if sign(prev_pick, k):
                new_map[k] = pow(score, self.directionality)
        weights = w.apply(new_map, weights)
        return w.ensure_safe(weights)
    
    def adjust_for_range(self, weights):
        for k in weights.keys():
            if k < self.noterange[0] or k > self.noterange[1]:
                del weights[k]
        return weights;
    
    def register_pick(self, pick):
        self.prev_picks.append(pick)
        self.prev_picks = self.prev_picks[-self.max_length:]
        if self.current_harmony is not None:
            self.current_harmony.register_pick(pick)
        
if __name__ == '__main__':
    lines = []
    l = LineMap(items=None, linearity=1, variance=2)
    
    for i in xrange(20):
        print l.pick()
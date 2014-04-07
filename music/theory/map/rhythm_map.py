from number_map import NumberMap
import weights as w

class RhythmMap(NumberMap):
    beats = 0
    balance = 1.
    uniformity = 10.
    
    def adjust(self, method="pick"):
        weights = super(RhythmMap, self).adjust(method)
        if self.balance != 0:
            weights = self.adjust_for_balance(weights)
        if self.uniformity != 0:
            weights = self.adjust_for_uniformity(weights)
        return weights
    
    def adjust_for_balance(self,weights):
        location = 0.
        ons = 0
        offs = 0
        new_map = {}
        for pick in self.prev_picks:
            location += pick
            if int(location) == location:
                ons += 1
            else:
                offs += 1
        #print "offs",offs,"ons",ons
        for k in weights:
            if int(k) != k and int(location) != location or int(k) == k and int(location) == location:
                new_map[k] = pow(2, offs-ons)
            else:
                new_map[k] = pow(2, ons-offs)
        
        weights = w.apply(new_map, weights)
        #print weights
        return w.ensure_safe(weights)
    
    def adjust_for_uniformity(self, weights):
        new_map = {}
        for k in weights.keys():
            occurrences = self.prev_picks.count(k)
            new_map[k] = pow(2, - self.uniformity * occurrences)
        weights = w.apply(new_map, weights)
        return w.ensure_safe(weights)
    
    def register_pick(self, pick):
        NumberMap.register_pick(self, pick)
        self.beats += pick

rm = RhythmMap({0.5:1, 1:1})

for i in range(10):
    print rm.pick()
    
from data_map import DataMap

class NumberMap(DataMap):
    gravity = 0 # > 0: pull selections together, < 0: push apart
    
    def adjust(self, method="pick"):
        weights = DataMap.adjust(self, method)
        if self.gravity != 0:
                weights = self.adjust_for_gravity(weights)
        return weights
        
    def adjust_for_gravity(self, weights):
        '''works similar to linearity, except considers all past choices equally'''
        prev_picks = self.prev_picks[-self.max_length:]
        if len(prev_picks) == 0: return weights
        for pick in prev_picks:
            for k,_ in weights.items():
                distance = abs(pick-k) + 1
                gravity_strength = 1. / pow(distance, self.gravity)
                weights[k] *= gravity_strength
            weights = self.ensure_safe_weights(weights)
        return weights


if (__name__ == '__main__'):
    d = NumberMap([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15], 10)
    d.gravity = 2
    print d.weighted_items
    
    counts = {}
    for i in range(0,1):
        selection = d.select(5)
        print selection
        #d.prev_picks = []
        for choice in selection:
            if choice in counts.keys():
                counts[choice] += 1
            else:
                counts[choice] = 1
        
        '''choice = d.pick()
        counts[choice] += 1'''
    #print counts
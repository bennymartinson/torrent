import random
from copy import copy
import weights as w

class DataMap(object):
    weighted_items = {}
    variance = 0 # > 0: less repetition than random, < 0: more
    prev_selections = []
    max_length = 0
    left_to_select = 1
    
    leads = {}
    
    def __init__(self, items = {}, **kwargs):
        self.setItems(items)
        self.prev_picks = []
        self.max_length = len(self.weighted_items) * 2 - 1
        for key in kwargs:
            setattr(self, key, kwargs[key])
    
    def setItems(self, items):
        if type(items) is list:
            self.weighted_items = {k : 1 for k in items}
        else:
            self.weighted_items = items
        if len(self.weighted_items):
            self.clean()
    
    def pick(self):
        ''' Pick a single item from the data'''
        weights = self.adjust("pick")
        choice = self.choose(weights)
        self.register_pick(choice)
        return choice
    
    def select(self, number):
        '''Select and return a collection of items from the data'''
        selection = []
        self.left_to_select = number + 1
        for _ in range(number):
            self.left_to_select -= 1
            weights = self.adjust("select")
            choice = self.choose(weights)
            selection.append(choice)
            self.register_pick(choice)
        self.prev_picks = []
        return selection
    
    def adjust(self, method="pick"):
        weights = copy(self.weighted_items)
        if self.variance != 0:
            weights = self.adjust_for_variance(weights)
        if method == "pick":
            if len(self.leads):
                weights = self.adjust_for_leads(weights)
        elif method == "select":
            pass
        return weights
        
    def adjust_for_variance(self, weights):
        map = {}
        prev_picks = self.prev_picks[-self.max_length:]
        prev_picks_length = len(self.prev_picks)
        for k in weights.keys():
            occurrence_score = sum([1/pow(prev_picks_length - index, 0.5) 
                                    for index,val in enumerate(self.prev_picks) if self.identity(k, val)])
            map[k] = pow(2, (- self.variance * occurrence_score))
        return w.ensure_safe(w.apply(map, weights))
        
    def adjust_for_leads(self, weights):
        map = {}
        if len(self.prev_picks) == 0: return weights
        prev = self.prev_picks[-1]
        if (prev not in self.leads.keys()): return weights
        leadChoices = self.leads[prev]
        if len(set(leadChoices.keys()).union(weights.keys())) == 0:
            return weights # lead choices and weights have no options in common
        for k,v in weights.items():
            if k in leadChoices:
                map[k] = v
            else:
                map[k] = 0
        return w.ensure_safe(w.apply(map, weights))
    
    def register_pick(self, pick):
        self.prev_picks.append(pick)
        max_length = 2 * len(self.weighted_items) - 1
        self.prev_picks = self.prev_picks[0-max_length:] #keep only max_length most recent
    
    @staticmethod
    def choose(weights):
        '''Choose one item out of a weighted list.'''
        weights = w.probabilitize(weights)
        rand = random.random()
        choice = None
        for k, v in weights.items():
            if rand <= v:
                choice = k
                break;
            rand = rand - v
        return choice
    
    ### Utility functions
    @staticmethod
    def identity(x, y): # to be overrided when dealing with pitch classes
        return x == y
    
    ### Cleaning operations
    def clean(self):
        self.max_length = len(self.weighted_items) * 2 - 1
        self.normalize()
    
    def normalize(self):
        self.weighted_items = w.normalize(self.weighted_items)

if __name__ == '__main__':
    dm = DataMap({1:0.001, 2:1, 3:5})
    weights = dm.weighted_items
    print weights
    print w.scale(weights, 0.1)
    
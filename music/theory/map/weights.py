from random import random

def apply(apply_weight, to_weight):
    """apply only as much weight as is not already present"""
    apply_amt = 1
    ret = {}
    for k in apply_weight.keys():
        if k in to_weight:
            ret[k] = apply_weight[k] * to_weight[k]
    return ret
    

def ensure_safe(weights):
    '''Set weights values to 1 if all are 0 and make sure size doesn't get too big or small'''
    sum_weights = sum(weights.values())
    if sum_weights == 0:
        raise Exception("uh-oh, zeroed out weights!!")
        return {k : 1 for k in weights.keys()}
    elif sum_weights < 0.01 or sum_weights > 1000000:
        return normalize(weights, False)
    else:
        return weights
    
def scale(weights, factor):
    for item,weight in weights.items():
        weights[item] = pow(weight, factor)
    return normalize(weights)

def multiply(weights1, weights2):
    ret = {}
    for item,weight in weights1.items():
        if item in weights2:
            ret[item] = weight * weights2[item]
    return ret

def exp(weights, amt):
    return {k:pow(v, amt) for k,v in weights.items()}

def normalize(weights, ensure = True):
    """Scale weights so that all add up to number of items."""
    num_weights = len(weights)
    if ensure:
        weights = ensure_safe(weights)
    total_weight = sum(weights.values())
    if total_weight == num_weights:
        return weights
    return {k : float(v) / total_weight * num_weights for k, v in weights.items()}
    
def probabilitize(weights):
    total_weight = sum(weights.values())
    if total_weight == 1:
        return weights
    return {k : float(v) / total_weight for k, v in weights.items()}

def choose(weights):
    '''Choose one item out of a weighted list.'''
    weights = probabilitize(weights)
    rand = random()
    choice = None
    for k, v in weights.items():
        if rand <= v:
            choice = k
            break;
        rand = rand - v
    return choice
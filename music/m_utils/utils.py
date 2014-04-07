import random

def pick(list):
    return list[random.randint(0, len(list)-1)]

def scale_val(a, x1, x2, y1, y2):
    multiplier = (float(y2) - y1) / (x2 - x1)
    return (a - x1) * multiplier + y1

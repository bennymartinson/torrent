"""A musical line, calculated using a sequence of harmonies"""
from music.theory.sequence import Sequence
from random import choice

class Line(Sequence):
    pass

if (__name__ == '__main__'):
    l = Line()
    for i in xrange(10):
        l.append(choice([60, 62, 64, 66, 67, None]), choice([1, 2]))
        
    print l.items
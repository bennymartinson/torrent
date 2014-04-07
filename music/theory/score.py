'''Keeps track of and coordinates all measures, harmonies, and lines.'''
from music.theory.pitch import harmony
from music.theory.time import measure

class Score:
    harmonies = []
    measures = []
    
    def __init__(self)
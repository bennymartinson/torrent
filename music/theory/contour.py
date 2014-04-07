from copy import copy

class Contour:
    data = []
    def __init__(self, *args):
        self.data = args
        self.clean()
    
    def clean(self):
        self.normalize();
    
    def normalize(self):
        datacopy = list(set(copy(self.data)))
        datacopy.sort()
        self.data = [datacopy.index(item) for item in self.data]
        

class Meter:
    numerator = 4
    denominator = 4
    
    def __init__(self, numerator=4, denominator=4):
        self.numerator = numerator
        if not is_power_of_2(denominator):
            raise Exception("denominator is not a power of 2")
        self.denominator = denominator
    
    def duration(self):
        return float(numerator) / denominator
    
    def clean(self):
        if not is_power_of_2(self.denominator):
            raise Exception("denominator is not a power of 2")

def is_power_of_2(x):
    return x & (x-1) == 0
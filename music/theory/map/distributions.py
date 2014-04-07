def curve(x):
    ret = 1-abs(x)
    return max(0, ret)

def exp_shape(func, factor):
    def ret(x):
        return pow(func(x), factor)
    return ret

def stretch(func, stretchx, stretchy):
    def ret(x):
        return stretchy * func(x/float(stretchx))
    return ret

def offset(func, offsetx, offsety):
    def ret(x):
        return offsety + func(x - offsetx)
    return ret

def lopside(func, amt):
    def ret(x):
        if x < amt:
            x = scale_val(x, -1, amt, -1, 0)
        else:
            x = scale_val(x, amt, 1, 0, 1)
        return func(x)
    return ret


def scale_val(a, x1, x2, y1, y2):
    multiplier = (float(y2) - y1) / (x2 - x1)
    return (a - x1) * multiplier + y1

newcurve = exp_shape(lopside(curve, 0.5), 0.5)
for x in range(-10, 11):
    print x/10., newcurve(x/10.)
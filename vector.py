import math

def Sum(*vectors):
    varvals = zip(*vectors)
    return [sum(var) for var in varvals]

def Average(*vectors):
    vecsum = Sum(*vectors)
    return Scale(vecsum, 1./len(vectors))

def Subtract(v1, v2):
    return Sum(v1, Scale(v2, -1))

def Magnitude(vector):
    return sum([a**2 for a in vector])**0.5

def SubVector(vector, *indices):
    """Create a new vector out of any number of this vector's dimensions"""
    return tuple([vector[index] for index in indices])

def Distance(v1, v2):
    return Magnitude(Sum(v1, Scale(v2, -1)))

def Determinant(*vectors):
    """Calculates the determinant of 2-dimensional vectors"""
    if len(vectors) == 2:
        return vectors[0][0]*vectors[1][1] - vectors[0][1]*vectors[1][0]
    else:
        raise Exception("not yet able to find determinant of vector of length != 2")

def Area(*points):
    """Calculates the Area within any number of 2-dimensional points"""
    ret = 0.
    for i in range(len(points)-1):
        ret += Determinant(points[i], points[i+1])
    return abs(ret * .5)


def DotProduct(v1, v2):
    if len(v1) != len(v2):
        raise VectorDimensionException('The vectors given do not have equal lengths!')
    return sum([v1[i] * v2[i] for i in range(len(v1))])

def Angle(v1, v2):
    """ Calculates the angle between 2 vectors in n-dimensional space """
    v1 = UnitVector(v1)
    v2 = UnitVector(v2)
    dp = max(min(DotProduct(v1, v2), 1), -1)
    return math.degrees(math.acos(dp))

def Center(points):
    xs, ys, zs = zip(*points)
    avgx = sum(xs)/float(len(xs))
    avgy = sum(ys)/float(len(ys))
    avgz = sum(zs)/float(len(zs))
    xs = [x-avgx for x in xs]
    ys = [y-avgy for y in ys]
    zs = [z-avgz for z in zs]
    return zip(xs, ys, zs), (avgx, avgy, avgz)

def Flatten(points):
    """ Rotates a set of points to the nearest x,y coordinates """
    ret = []
    for point in points:
        mag = Magnitude(point)
        x,y,_ = UnitVector(point)
        unit2d = x,y
        ret.append(Scale(unit2d, mag))
    return ret

def UnitVector(vector):
    """Creates a unit vector from a vector."""
    mag = Magnitude(vector)
    mult = 1./mag
    x,y,z = vector
    return (x*mult, y*mult, z*mult)

def Scale(vector, mag):
    """Scales a unit vector to the specified magnitude."""
    return tuple([x*mag for x in vector])

class VectorDimensionException(Exception):
    pass

if __name__ == '__main__':
    print Angle((1,1,1), (1,1,1)) / math.pi
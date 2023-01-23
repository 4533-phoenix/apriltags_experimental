import numpy

def inverse(A: numpy.ndarray) -> numpy.ndarray:
    return numpy.linalg.inv(A.transpose(2,0,1)).transpose(1,2,0)
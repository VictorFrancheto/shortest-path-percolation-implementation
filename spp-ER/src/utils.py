
#Importing libaries
import sys
import time
import os
import math
import random

####################################
#      Mersenne Twister 64-bit     #
# (or placeholder with random below)
####################################

NN = 312
mt = [0]*NN
mti = 0

def genrand64_int64():
    """
    In C, there would be a real implementation of the 64-bit Mersenne Twister.
    Here, we use a placeholder with random.getrandbits(64).
    If you want identical behavior, implement the full MT64.
    """
    return random.getrandbits(64)

def genrand64_real3():
    """
    In C: ((genrand64_int64() >> 12) + 0.5) * (1.0 / 4503599627370496.0).
    Placeholder using 64-bit random bits:
    """
    return genrand64_int64() / float(1 << 64)

def init_genrand64(seed):
    """
    Initialize the generator with a 64-bit seed.
    This function follows the standard initialization procedure
    used in the Mersenne Twister algorithm.
    """
    global mt, mti
    mt[0] = seed
    for mti in range(1, NN):
        mt[mti] = (6364136223846793005 * (mt[mti - 1] ^ (mt[mti - 1] >> 62)) + mti) & ((1 << 64) - 1)
        

#Author: Matt Myers

import numpy
import os
import sys
from getopt import getopt, GetoptError
from datetime import datetime
import random


populations = {'Pop_Rock':1926,
                'Electronic':228,
                'Rap':236,
                'Jazz':173,
                'Latin':257,
                'RnB':132,
                'International':147,
                'Country':175,
                'Religious':198,
                'Reggae':120,
                'Blues':126,
                'Vocal':36,
                'Folk':48,
                'New':95,
                'Comedy_Spoken':39,
                'Stage':30,
                'Easy_Listening':20,
                'Avant_Garde':10,
                'Classical':6,
                'Children':7,
                'Holiday':2}

class Sampler:

    def __init__(self):
        self.generator = {}
        i = 0
        for key, value in populations:
            for _ in range(value):
                self.generator[i] = key
                i += 1
        random.seed(1)


def main(argv):
    def usage():
        print "[]"
    try:
        opts, args = getopt(argv, "", [""])                         
    except GetoptError:           
        usage()                         
        sys.exit(2)  
    for opt, arg in opts:
        pass

    print datetime.now(), "Start"

    props = {}
    for key,value in populations:

    

    print datetime.now(), "End"

if __name__ == "__main__":
    main(sys.argv[1:])

# C:\\Users\\Matt\\Documents\\-5- Fall 2015\\CMSC396h project\\MillionSongSubset\\data\\A\\A\\A
# TRAAAAW128F429D538.h5
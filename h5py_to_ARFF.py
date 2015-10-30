import numpy
from scipy import stats
import h5py
import glob
import os
import sys
from getopt import getopt
from datetime import datetime
from csv import writer

def get_stats(myList):
    a = numpy.array(myList, dtype = 'f')
    return [numpy.mean(a), numpy.median(a), numpy.var(a), numpy.min(a), numpy.max(a), stats.skew(a), stats.kurtosis(a)]
def generate_headers(s):
    return ["%s-mean" % s,"%s-med" % s,"%s-var" % s,
            "%s-min" % s,"%s-max" % s,"%s-skw" % s,"%s-krt" % s ]
def main(argv):
    def usage():
        print "[]"
    try:
        opts, args = getopt(argv, "-c", [""])                         
    except GetoptError:           
        usage()                         
        sys.exit(2)  
    for opt, arg in opts:
        if opt == "-c":
            os.chdir(arg)    

    print datetime.now()
    os.chdir('C:\\Users\\Matt\\Documents\\-5- Fall 2015\\CMSC396h project\\MillionSongSubset\\data')
    header_categories =['pitches0','pitches1','pitches2','pitches3','pitches4','pitches5','pitches6','pitches7','pitches8','pitches9','pitches10','pitches11', 'timbre0', 'timbre1','timbre2','timbre3','timbre4','timbre5','timbre6','timbre7','timbre8','timbre9','timbre10','timbre11', 'loudmax']
    headers = []
    for h in header_categories:
        temp_h = generate_headers(h)
        for h1 in temp_h:
            headers.append("ATTRIBUTE %s NUMERIC" % h1)
    output = open('data.arff', 'w')
    output.write("\n".join(headers))
    output.write("\n")

    matt_path = 'C:\\Users\\Matt\\Documents\\-5- Fall 2015\\CMSC396h project\\MillionSongSubset\\data'

    files = []
    for dir, path, name in os.walk(matt_path):
        if str(name).endswith('.h5'):
            files.append(os.path.join(dir, name))

    data = []
    print len(files)
    for fname in files:
        features = []
        f = h5py.File(fname, 'r')
        db = f['analysis']

        pitches = db['segments_pitches']
        timbre = db['segments_timbre']
        loudmax = db['segments_loudness_max']


        for i in range(12):
            r = get_stats([x[i] for x in pitches])
            features.extend(r)
        for i in range(12):
            r = get_stats([x[i] for x in timbre])
            features.extend(r)
        features.extend(get_stats[loudmax])
        
        print len(features)
        output.write(features)
        break
#        loudmaxtime = db['segments_loudness_max_time'] # might not be correct
#        length = db['segments_start']

    output.close()

if __name__ == "__main__":
    main(sys.argv[1:])

# C:\\Users\\Matt\\Documents\\-5- Fall 2015\\CMSC396h project\\MillionSongSubset\\data\\A\\A\\A
# TRAAAAW128F429D538.h5
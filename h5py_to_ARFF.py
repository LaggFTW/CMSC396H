#Author: Matt Myers

import numpy
from scipy import stats
import h5py
import glob
import os
import sys
from getopt import getopt
from datetime import datetime
from csv import writer

matt_path = 'C:\\Users\\Matt\\Documents\\-5- Fall 2015\\CMSC396h project\\MillionSongSubset\\data\\'
matt_genres_path = 'C:\\Users\\Matt\\Documents\\-5- Fall 2015\\CMSC396h project'

def get_stats(myList):
    a = numpy.array(myList, dtype = 'f')
    g_opt = False
    ofile = 'data.arff'
    return [numpy.mean(a), numpy.median(a), numpy.var(a), numpy.min(a), numpy.max(a), stats.skew(a), stats.kurtosis(a)]
def generate_headers(s):
    return ["%s-mean" % s,"%s-med" % s,"%s-var" % s,
            "%s-min" % s,"%s-max" % s,"%s-skw" % s,"%s-krt" % s ]
def main(argv):
    def usage():
        print "[-g for Allmusic genres]"
    try:
        opts, args = getopt(argv, "-g", [""])                         
    except GetoptError:           
        usage()                         
        sys.exit(2)  
    for opt, arg in opts:
        if opt == "-g":
            g_opt = True
            ofile = 'genres_data.arff'

    print datetime.now(), "Start"

    #### Make this the path to (and including) your own /data folder
    
    os.chdir(matt_path)

    #Initializes headers and writes header information to .arff file
    header_categories =['pitches0','pitches1','pitches2','pitches3','pitches4','pitches5','pitches6','pitches7','pitches8','pitches9','pitches10','pitches11', 'timbre0', 'timbre1','timbre2','timbre3','timbre4','timbre5','timbre6','timbre7','timbre8','timbre9','timbre10','timbre11', 'loudmax']
    headers = []
    genres_h = ['Pop_Rock', 'Electronic', 'Rap', 'Jazz', 'Latin', 'RnB', 'International', 'Country', 'Religious', 'Reggae', 'Blues', 'Vocal', 'Folk', 'New', 'Comedy_Spoken', 'Stage', 'Easy_Listening', 'Avant_Garde', 'Classical', 'Children', 'Holiday']
    genres_header = "\n@ATTRIBUTE genre {%s}\n" % ",".join(genres_h)

    for h in header_categories:
        temp_h = generate_headers(h)
        for h1 in temp_h:
            headers.append("@ATTRIBUTE %s NUMERIC" % h1)
    output = open(ofile, 'wb')
    output.write('@RELATION song\r\n')
    output.write('@ATTRIBUTE ID STRING\r\n')
    output.write("\n".join(headers))
    output.write('\r\n@ATTRIBUTE key NUMERIC\r\n')
    output.write('@ATTRIBUTE mode NUMERIC\r\n')

    if g_opt:
        output.write(genres_header)

    output.write("@DATA\n")


    #Collects files in the current directory
    files = []
    for dir, paths, names in os.walk("."):
        for name in names:
            if name.endswith('.h5'):
                files.append(os.path.join(dir, name))

    data = []

    counter = 0

    # Opens the Allmusic_Genre_Subset.txt file to select only files that have genres associated with them
    # NOTE: will need to update path if the file isn't here
    if g_opt:
        genres = {}
        valid_files = []
        os.chdir(matt_genres_path)
        gfile = open('Allmusic_Genre_Subset.txt', 'rb')
        for line in gfile:
            l = line.split()
            genres[l[0]] = l[1]
        for fname in files:
            if genres.has_key(fname.split('.')[1].split('\\')[-1]):
                valid_files.append(fname)
        files = valid_files
        os.chdir(matt_path)
    
    print len(files)
    print len(headers)
    
    for fname in files:
        if counter % 100 == 0:
            print datetime.now(), "Starting instance %d" % counter
        counter += 1


        features = []
        features.append(fname.split('.')[1].split('\\')[-1])
        f = h5py.File(fname, 'r')
        db = f['analysis']

        pitches = db['segments_pitches']
        timbre = db['segments_timbre']
        loudmax = db['segments_loudness_max']
#        loudmaxtime = db['segments_loudness_max_time'] # maybe should be relative to segment start time?
#        length = db['segments_start']
        
        key = db['songs'][0][21]
        mode = db['songs'][0][24]

        for i in range(12):
            norm_pitch = (i - key + 12) % 12
            r = get_stats([x[norm_pitch] for x in pitches])
            features.extend(r)
        for i in range(12):
            r = get_stats([x[i] for x in timbre])
            features.extend(r)
        
        features.extend(get_stats(loudmax))
        features.append(key)
        features.append(mode)

        if g_opt:
            features.append(genres[fname.split('.')[1].split('\\')[-1]])

        output.write(",".join([str(i) for i in features]))
        output.write("\n")

    output.close()
    print datetime.now(), "End"

if __name__ == "__main__":
    main(sys.argv[1:])

# C:\\Users\\Matt\\Documents\\-5- Fall 2015\\CMSC396h project\\MillionSongSubset\\data\\A\\A\\A
# TRAAAAW128F429D538.h5
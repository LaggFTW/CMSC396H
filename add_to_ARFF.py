import os
from getopt import getopt, GetoptError
import sys
import h5py
import feature_extract as ftex
import numpy 
from datetime import datetime

matt_path = 'C:\\Users\\Matt\\Documents\\-5- Fall 2015\\CMSC396h project\\MillionSongSubset\\data\\'

# Takes in an existing ARFF file, finds the matching HDF5 file for each instance, does additional analysis to generate more features, and creates a new ARFF file with the additional features appended to the header and to each instance

# auxiliary functions
def generate_headers(s):
    return ["%s-mean" % s,"%s-med" % s,"%s-var" % s,
            "%s-min" % s,"%s-max" % s,"%s-skw" % s,"%s-krt" % s]
def generate_rep_headers(s, sectwise=False):
    if sectwise:
        return ["%s-posmin" % s, "%s-posmax" % s, "%s-posmean" % s, "%s-posvar" % s, "%s-posskw" % s, "%s-poskrt" % s,
                "%s-negmin" % s, "%s-negmax" % s, "%s-negmean" % s, "%s-negvar" % s, "%s-negskw" % s, "%s-negkrt" % s]
    else:
        return ["%s-argmax" % s, "%s-max" % s, "%s-argmin" % s, "%s-min" % s,
                "%s-mean" % s, "%s-med" % s, "%s-var" % s, "%s-skw" % s,"%s-krt" % s]

def main(argv):
    def usage():
        print "[.ARFF file]"
    try:
        opts, args = getopt(argv, "", [""]) 
        ifile = open(argv[0], 'rb')             
    except GetoptError:           
        usage()                         
        sys.exit(2)  
    for opt, arg in opts:
        pass

    print datetime.now(), "Start"


    output = open('modified_data.arff', 'wb')
    additional_headers = []
    headers_done = False
    fname = argv[0] 

    ###### headers for each feature are appended here
    
    # segment duration statistics (7 features)
    additional_headers.extend(generate_headers('seglen'))
    
    # section duration statistics (7 features)
    additional_headers.extend(generate_headers('sectlen'))
    
    # chord-based features (7 + 7 + 2 = 16 features)
    additional_headers.extend(generate_headers('chordsize'))
    additional_headers.extend(generate_headers('chordfreq'))
    additional_headers.extend(['noisiness','uniqchord-ct'])
    
    # repetition features (12 * (9 + 12 + 12) = 396 features)
    for i in range(0,12):
        additional_headers.extend(generate_rep_headers('rep%i' % i)) # overall
        additional_headers.extend(generate_rep_headers('intra%i' % i, sectwise=True)) # intra-section
        additional_headers.extend(generate_rep_headers('inter%i' % i, sectwise=True)) # inter-section
    
    ## add attribute tags
    additional_headers = map(lambda x: "@ATTRIBUTE %s NUMERIC" % x, additional_headers)

    ###### Change this value to the path to your MillionSongSubset/data folder
    os.chdir(matt_path)
    files = {}

    for dir, paths, names in os.walk("."):
        for name in names:
            if name.endswith('.h5'):
                files[name.split('.')[0].split('\\')[-1]] = os.path.join(dir, name)

    c = 0
    broken = 0
    for line in ifile:
        if not headers_done and (line[0] == '@' or line[0] == '\n' or line[0] == ' '):
            output.write(line)
            continue
        else:
            if not headers_done:
                # We just finished the header lines, so we add the new headers
                headers_done = True
                output.write('\n'.join(additional_headers))
                output.write('\r\n\n@DATA\r\n')
            elif len(line.split(',')) < 2:
                # We're between headers and data, so pass (already wrote @DATA)
                pass
            else:
                c += 1
                if c % 100 == 0:
                    print datetime.now(), "Beginning instance %d" % c

                # Adding data to instances
                id = line.split(',')[0]
                f = h5py.File(files[id], 'r')
                db = f['analysis']
                
                key = db['songs'][0][21]
                duration = db['songs'][0][3]
                pitches = db['segments_pitches'] # TODO: perform key / mode normalization here
                timbre = db['segments_timbre']
                seg_start = db['segments_start']
                sect_start = db['sections_start']
                
                ###### compute additional data here
                additional_data = []
                
                # segment duration statistics
                additional_data.extend(ftex.gen_stats(numpy.array(ftex.event_durations(seg_start, duration, norm=True), dtype='f')))
                # section duration statistics
                additional_data.extend(ftex.gen_stats(numpy.array(ftex.event_durations(sect_start, duration, norm=True), dtype='f')))
                # chord-based features
                additional_data.extend(ftex.chord_features(pitches))
                # repetition features
                sect_parts = ftex.partition_segments(sect_start, seg_start, duration)
                if len(sect_parts) == 0: 
                    broken += 1
                    continue
                for i in range(0,12):
                    t_i = [x[i] for x in timbre]
                    additional_data.extend(ftex.overall_rep_features(t_i))
                    additional_data.extend(ftex.intra_sect_rep_features(t_i, sect_parts))
                    additional_data.extend(ftex.inter_sect_rep_features(t_i, sect_parts))
                # 

                output.write("%s,%s" % (line.rstrip(), ','.join([str(i) for i in additional_data])))
                output.write('\n')

    output.close()

    print datetime.now(), "End"
    print "broken = %d" % broken

if __name__ == "__main__":
    main(sys.argv[1:])


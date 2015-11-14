import os
import getopt
import sys
import h5py

matt_path = 'C:\\Users\\Matt\\Documents\\-5- Fall 2015\\CMSC396h project\\MillionSongSubset\\data\\'
# Takes in an existing ARFF file, finds the matching HDF5 file for each instance, does additional analysis to generate more features, and creates a new ARFF file with the additional features appended to the header and to each instance

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

    output = open('modified_data.arff', 'wb')
    additional_headers = []
    headers_done = False

    ###### Change this value to the path to your MillionSongSubset/data folder
    os.chdir(matt_path)
    files = {}
    for dir, paths, names in os.walk("."):
        for name in names:
            if name.endswith('.h5'):
                files[fname.split('.')[1].split('\\')[-1]] = os.path.join(dir, name)


    for line in ifile:
        if not headers_done and line[0] == '@':
            continue
        else:
            if not headers_done:
                # We just finished the header lines, so we add the new headers
                headers_done = True
                output.write('\n'.join(additional_headers))
            elif len(line.split(',')) < 2:
                # We're at the lines between headers and data, so copy them over
                output.write('%s\n' % line)            
            else:
                # Adding data to instances
                id = line.split(',')[0]
                f = h5py.File(files[id], 'r')
                
                additional_data = []
                #Create additional data here
                
                #

                output.write(line)
                output.write(',')
                output.write(','.join(additional_data))
                output.write('\n')

    output.close()



if __name__ == "__main__":
    main(sys.argv[1:])
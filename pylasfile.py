#name:          pylasfile
#created:       July 2017
#by:            p.kennedy@fugro.com
#description:   python module to read and write a ASPRS LAS file natively
#notes:         See main at end of script for example how to use this
#based on ASPRS LAS 1.4-R13 15 July 2013


# See readme.md for more details

# LAS FORMAT DEFINITION:
# The format contains binary data consisting of 
# A public header block, 
# Any number of (optional) Variable Length Records (VLRs)
# The Point Data Records
# Any number of (optional) Extended Variable Length Records (EVLRs). 
# 
# All data are in little-endian format. 
# The public header block contains generic data such as point numbers and point data bounds. 

import os.path
import struct
import sys


def main():
    #open the ALL file for reading by creating a new ALLReader class and passin in the filename to open.
    # filename =   "C:/Python27/ArcGIS10.3/pyall-master/em2000-0017-e_007-20111101-093632.all"
    # filename =   "C:/development/Python/m3Sample.all"
    filename = "C:/development/python/sample.las"
    r = lasreader(filename)
    r.readhdr()



class lasreader:

    def __init__(self, filename):
        if not os.path.isfile(filename):
            print ("file not found:", filename)
        self.fileName = filename
        self.fileptr = open(filename, 'rb')        
        self.fileSize = os.path.getsize(filename)
        # self.recordDate = ""
        # self.recordTime = ""

    def close(self):
        self.fileptr.close()
        
    def rewind(self):
        # go back to start of file
        self.fileptr.seek(0, 0)                

    def readhdr(self):

        hdrfmt = "4sHHLHH8BBB323232HHLLBHL5LddddddddddddQQLQ15Q"
        hdrlen = struct.calcsize(hdrfmt)
        # hdrunpack = struct.Struct(hdrfmt).unpack_from

        # curr = self.fileptr.tell()
        data = self.fileptr.read(hdrlen)
        s = struct.unpack(hdrfmt, data)
        print(s[0])

if __name__ == "__main__":
        main()

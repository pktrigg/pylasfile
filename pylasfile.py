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
import pprint
import time
import datetime
from collections import OrderedDict

def main():

    # testreader()
    testwriter()

def testwriter():

    outFileName = os.path.join(os.path.dirname(os.path.abspath("c:/development/python/laswriter.las")), "laswriter.las")
    outFileName = createOutputFileName(outFileName)
    writer = laswriter(outFileName)
    writer.writeHeader()
    writer.close()

def testreader():
    start_time = time.time() # time the process so we can keep it quick

    filename = "C:/development/python/sample.las"
    filename = "C:/development/python/version1.4_format0.las"
    # create a lasreader class and pass the filename
    r = lasreader(filename)
    # r.read the header
    r.readhdr()

    # print some metadata about the reader
    print (r)

    # read the variable records
    for i in range(r.hdr.parameters['NumberofVariableLengthRecords']):
        r.readvariablelengthrecord()

    # now find the start point for the point records
    r.seekPoints()
    # read the point data
    points = r.readpointrecords(64)
    # points = r.readpointrecords(r.hdr.parameters['Numberofpointrecords'])

    for p in points:
        print ("%.3f, %.3f %.3f" % ((p[0] * r.hdr.Xscalefactor) + r.hdr.Xoffset, (p[1] * r.hdr.Yscalefactor) + r.hdr.Yoffset, (p[2] * r.hdr.Zscalefactor) + r.hdr.Zoffset))

    print("Duration %.3fs" % (time.time() - start_time )) # time the process

    return

###############################################################################
class laswriter:
    def __init__(self, filename):
        self.fileName = filename
        self.fileptr = open(filename, 'wb')        
        self.hdr = lashdr()

    def close(self):
        self.fileptr.close()
        
    def rewind(self):
        # go back to start of file
        self.fileptr.seek(0, 0)                

    def seekPoints(self):
        # set the file pointer to the start of the points block
        self.fileptr.seek(self.hdr.parameters['Offsettopointdata'], 0)                

    def writeHeader(self):
        # convert the header variables into a list, then conver the list into a tuple so we can pack it
        hdrList = self.hdr.parameters.values()
        values = tuple(hdrList)
        s = struct.Struct(self.hdr.hdrfmt)
        data = s.pack(*values)
        self.fileptr.write(data)

###############################################################################
class lashdr:
    def __init__(self):

        # version 1.4 header format
        self.hdrfmt = "<4sHHL HH8sBB 32s32sHHH LLBHL 5Ldddd ddddd dddQQ LQ15Q"
        # self.hdrfmt = "<4sHHL HH8sBB 32s32sHHH LLBHL 5Ldddd ddddd dddQQ LQ15Q"
        self.hdrlen = struct.calcsize(self.hdrfmt)

        # create a default template for a V1.4 header.  We use this for writing purposes
        hdr = OrderedDict()
        hdr["FileSignature"] =                        b'LASF'
        hdr['FileSourceID'] =                         0
        hdr ["GlobalEncoding"] =                      17
        hdr ["ProjectIDGUIDdata1"] =                  0
        
        hdr ["ProjectIDGUIDdata2"] =                  0
        hdr ["ProjectIDGUIDdata3"] =                  0
        hdr ["ProjectIDGUIDdata4"] =                  b"12345678"

        hdr ["VersionMajor"] =                        1
        hdr ["VersionMinor"] =                        4
        hdr ["SystemIdentifier"] =                    b'pylasfile writer'
        hdr ["GeneratingSoftware"] =                  b'pylasfile writer'
        hdr ["FileCreationDayofYear"] =               datetime.datetime.now().timetuple().tm_yday
        hdr ["FileCreationYear"] =                    datetime.datetime.now().year
        hdr ["HeaderSize"] =                          375
        hdr ["Offsettopointdata"] =                   375
        hdr ["NumberofVariableLengthRecords"] =       0
        hdr ["PointDataRecordFormat"] =               1
        hdr ["PointDataRecordLength"] =               28
        hdr ["LegacyNumberofpointrecords"] =          0
        hdr ["LegacyNumberofpointsbyreturn1"] =       0
        hdr ["LegacyNumberofpointsbyreturn2"] =       0
        hdr ["LegacyNumberofpointsbyreturn3"] =       0
        hdr ["LegacyNumberofpointsbyreturn4"] =       0
        hdr ["LegacyNumberofpointsbyreturn5"] =       0
        hdr ["Xscalefactor"] =                        1
        hdr ["Yscalefactor"] =                        1
        hdr ["Zscalefactor"] =                        1
        hdr ["Xoffset"] =                             0
        hdr ["Yoffset"] =                             0
        hdr ["Zoffset"] =                             0
        hdr ["MaxX"] =                                0
        hdr ["MinX"] =                                0
        hdr ["MaxY"] =                                0
        hdr ["MinY"] =                                0
        hdr ["MaxZ"] =                                0
        hdr ["MinZ"] =                                0
        hdr ["StartofWaveformDataPacketRecord"] =     0
        hdr ["StartoffirstExtendedVariableLengthRecord"] =    0
        hdr ["NumberofExtendedVariableLengthRecords"]   = 0
        hdr ["Numberofpointrecords"] =                        0
        hdr ["Numberofpointsbyreturn1"] =             0  
        hdr ["Numberofpointsbyreturn2"] =             0  
        hdr ["Numberofpointsbyreturn3"] =             0  
        hdr ["Numberofpointsbyreturn4"] =             0  
        hdr ["Numberofpointsbyreturn5"] =             0  
        hdr ["Numberofpointsbyreturn6"] =             0  
        hdr ["Numberofpointsbyreturn7"] =             0  
        hdr ["Numberofpointsbyreturn8"] =             0  
        hdr ["Numberofpointsbyreturn9"] =             0  
        hdr ["Numberofpointsbyreturn10"] =             0  
        hdr ["Numberofpointsbyreturn11"] =             0  
        hdr ["Numberofpointsbyreturn12"] =             0  
        hdr ["Numberofpointsbyreturn13"] =             0  
        hdr ["Numberofpointsbyreturn14"] =             0  
        hdr ["Numberofpointsbyreturn15"] =             0  

        # make it public
        self.parameters = hdr

    def decodehdr(self, data):
        s = struct.unpack(self.hdrfmt, data)

        hdr = {}
        hdr["FileSignature"] =                        s[0]
        hdr['FileSourceID'] =                         s[1]
        hdr ["GlobalEncoding"] =                      s[2]
        hdr ["ProjectIDGUIDdata1"] =                  s[3]
        hdr ["ProjectIDGUIDdata2"] =                  s[4]
        hdr ["ProjectIDGUIDdata3"] =                  s[5]
        hdr ["ProjectIDGUIDdata4"] =                  s[6]
        hdr ["VersionMajor"] =                        s[7]
        hdr ["VersionMinor"] =                        s[8]
        hdr ["SystemIdentifier"] =                    s[9]
        hdr ["GeneratingSoftware"] =                  s[10]
        hdr ["FileCreationDayofYear"] =               s[11]
        hdr ["FileCreationYear"] =                    s[12]
        hdr ["HeaderSize"] =                          s[13]
        hdr ["Offsettopointdata"] =                   s[14]
        hdr ["NumberofVariableLengthRecords"] =       s[15]
        hdr ["PointDataRecordFormat"] =               s[16]
        hdr ["PointDataRecordLength"] =               s[17]
        hdr ["LegacyNumberofpointrecords"] =          s[18]
        hdr ["LegacyNumberofpointsbyreturn1"] =       s[19]
        hdr ["LegacyNumberofpointsbyreturn2"] =       s[20]
        hdr ["LegacyNumberofpointsbyreturn3"] =       s[21]
        hdr ["LegacyNumberofpointsbyreturn4"] =       s[22]
        hdr ["LegacyNumberofpointsbyreturn5"] =       s[23]
        hdr ["Xscalefactor"] =                        s[24]
        hdr ["Yscalefactor"] =                        s[25]
        hdr ["Zscalefactor"] =                        s[26]
        hdr ["Xoffset"] =                             s[27]
        hdr ["Yoffset"] =                             s[28]
        hdr ["Zoffset"] =                             s[29]
        hdr ["MaxX"] =                                s[30]
        hdr ["MinX"] =                                s[31]
        hdr ["MaxY"] =                                s[32]
        hdr ["MinY"] =                                s[33]
        hdr ["MaxZ"] =                                s[34]
        hdr ["MinZ"] =                                s[35]
        hdr ["StartofWaveformDataPacketRecord"] =     s[36]
        hdr ["StartoffirstExtendedVariableLengthRecord"] =    s[37]
        hdr ["NumberofExtendedVariableLengthRecords"] =       s[38]
        hdr ["Numberofpointrecords"] =                        s[39]
        hdr ["Numberofpointsbyreturn1"] =                     s[40]
        hdr ["Numberofpointsbyreturn2"] =                     s[41]
        hdr ["Numberofpointsbyreturn3"] =                     s[42]
        hdr ["Numberofpointsbyreturn4"] =                     s[43]
        hdr ["Numberofpointsbyreturn5"] =                     s[44]
        hdr ["Numberofpointsbyreturn6"] =                     s[45]
        hdr ["Numberofpointsbyreturn7"] =                     s[46]
        hdr ["Numberofpointsbyreturn8"] =                     s[47]
        hdr ["Numberofpointsbyreturn9"] =                     s[48]
        hdr ["Numberofpointsbyreturn10"] =                    s[49]
        hdr ["Numberofpointsbyreturn11"] =                    s[50]
        hdr ["Numberofpointsbyreturn12"] =                    s[51]
        hdr ["Numberofpointsbyreturn13"] =                    s[52]
        hdr ["Numberofpointsbyreturn14"] =                    s[53]
        hdr ["Numberofpointsbyreturn15"] =                    s[54]

        self.PointDataRecordFormat = hdr["PointDataRecordFormat"]

        self.Xscalefactor = hdr['Xscalefactor']
        self.Yscalefactor = hdr['Yscalefactor']
        self.Zscalefactor = hdr['Zscalefactor']
        self.Xoffset = hdr['Xoffset']
        self.Yoffset = hdr['Yoffset']
        self.Zoffset = hdr['Zoffset']

        hdrList = hdr.values()
        h = tuple(hdrList)

        self.parameters = hdr
    
###############################################################################
class lasreader:
    def __init__(self, filename):
        if not os.path.isfile(filename):
            print ("file not found:", filename)
        self.fileName = filename
        self.fileptr = open(filename, 'rb')        
        self.fileSize = os.path.getsize(filename)
        self.hdr = lashdr()

        # self.hdrfmt = "<4sHHLHH8sBB32s32sHHHLLBHL5LddddddddddddQQLQ15Q"
        # self.hdrlen = struct.calcsize(self.hdrfmt)

        # format 0
        self.ptfmt0 = "<lllHBBbBH"
        self.ptfmt0len = struct.calcsize(self.ptfmt0)
        # format 1
        self.ptfmt1 = "<lllHBBbBHd"
        self.ptfmt1len = struct.calcsize(self.ptfmt1)
        # self.hdr = {}

    def close(self):
        self.fileptr.close()
        
    def rewind(self):
        # go back to start of file
        self.fileptr.seek(0, 0)                

    def seekPoints(self):
        # set the file pointer to the start of the points block
        self.fileptr.seek(self.hdr.parameters['Offsettopointdata'], 0)                

    def __str__(self):
        return pprint.pformat(vars(self))

    def readhdr(self):
        data = self.fileptr.read(self.hdr.hdrlen)
        self.hdr.decodehdr(data)

    def readpointrecords(self, recordsToRead=1):
        if self.hdr.PointDataRecordFormat == 0:
            data = self.fileptr.read(self.ptfmt0len * recordsToRead)
            result = []
            i = 0
            for r in range(recordsToRead):
                j = i+self.ptfmt0len
                result.append(struct.unpack(self.ptfmt0, data[i:j]))
                i = j
            return result

        if self.hdr.PointDataRecordFormat == 1:
            data = self.fileptr.read(self.ptfmt1len * recordsToRead)
            result = []
            i = 0
            for r in range(recordsToRead):
                j = i+self.ptfmt1len
                result.append(struct.unpack(self.ptfmt1, data[i:j]))
                i = j
            return result

    # def readpointrecord(self, recordsToRead=1):
    #     if self.PointDataRecordFormat == 1:
    #         ptfmt = "<lllHBBbBHd"
    #         ptlen = struct.calcsize(ptfmt)
    #         data = self.fileptr.read(ptlen)
    #         s = struct.unpack(ptfmt, data)

    #         self.X                   = s[0]
    #         self.Y                   = s[1]
    #         self.Z                   = s[2]
    #         self.Intensity           = s[3]
    #         self.ReturnNumber        = s[4]
    #         self.NumberofReturns     = s[4]
    #         self.ScanDirectionFlag   = s[4]
    #         self.EdgeOfFlight        = s[4]
    #         self.Classification      = s[5]
    #         self.ScanAngleRank       = s[6]
    #         self.UserData            = s[7]
    #         self.PointSourceID       = s[8]
    #         self.GPSTime             = s[9]

    def readvariablelengthrecord(self):
        vlrhdrfmt = "<H16sHH32s"
        vlrhdrlen = struct.calcsize(vlrhdrfmt)
        data = self.fileptr.read(vlrhdrlen)
        s = struct.unpack(vlrhdrfmt, data)

        self.vlrReserved                   = s[0]
        self.vlrUserid                     = s[1]
        self.vlrrecordid                   = s[2]
        self.vlrRecordLengthAfterHeader    = s[3]
        self.vlrDescription                = s[4]

        # now read the variable data
        self.vlrdata = self.fileptr.read(self.vlrRecordLengthAfterHeader)
        print (self.vlrdata)


###############################################################################
def createOutputFileName(path):
     '''Create a valid output filename. if the name of the file already exists the file name is auto-incremented.'''
     path      = os.path.expanduser(path)

     if not os.path.exists(os.path.dirname(path)):
         os.makedirs(os.path.dirname(path))

     if not os.path.exists(path):
        return path

     root, ext = os.path.splitext(os.path.expanduser(path))
     dir       = os.path.dirname(root)
     fname     = os.path.basename(root)
     candidate = fname+ext
     index     = 1
     ls        = set(os.listdir(dir))
     while candidate in ls:
             candidate = "{}_{}{}".format(fname,index,ext)
             index    += 1

     return os.path.join(dir, candidate)



if __name__ == "__main__":
        main()

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

def main():
    start_time = time.time() # time the process so we can keep it quick
    filename = "C:/development/python/sample.las"
    r = lasreader(filename)
    r.readhdr()
    print (r)

    for i in range(r.hdr.parameters['NumberofVariableLengthRecords']):
        r.readvariablelengthrecord()

    # now find the start point for the point records
    r.seekPoints()
    points = r.readpointrecords(64)
    # points = r.readpointrecords(r.hdr['Numberofpointrecords'])

    for p in points:
        print ("%.3f, %.3f %.3f" % ((p[0] * r.hdr.Xscalefactor) + r.hdr.Xoffset, (p[1] * r.hdr.Yscalefactor) + r.hdr.Yoffset, (p[2] * r.hdr.Zscalefactor) + r.hdr.Zoffset))

    print("Duration %.3fs" % (time.time() - start_time )) # time the process

###############################################################################
class lashdr:
    def __init__(self):
        self.hdrfmt = "<4sHHLHH8sBB32s32sHHHLLBHL5LddddddddddddQQLQ15Q"
        self.hdrlen = struct.calcsize(self.hdrfmt)

        hdr = {}
        hdr["FileSignature"] =                        "LASF"
        hdr['FileSourceID'] =                         0
        hdr ["GlobalEncoding"] =                      17
        hdr ["ProjectIDGUIDdata1"] =                  0
        hdr ["ProjectIDGUIDdata2"] =                  0
        hdr ["ProjectIDGUIDdata3"] =                  0
        hdr ["ProjectIDGUIDdata4"] =                  0 #4 valuespkpk
        hdr ["VersionMajor"] =                        1
        hdr ["VersionMinor"] =                        4
        hdr ["SystemIdentifier"] =                    "pylasfile writer"
        hdr ["GeneratingSoftware"] =                  "pylasfile writer"
        hdr ["FileCreationDayofYear"] =               datetime.datetime.now().timetuple().tm_yday
        hdr ["FileCreationYear"] =                    datetime.datetime.now().year
        hdr ["HeaderSize"] =                          375
        hdr ["Offsettopointdata"] =                   375
        hdr ["NumberofVariableLengthRecords"] =       0
        hdr ["PointDataRecordFormat"] =               1
        hdr ["PointDataRecordLength"] =               1
        hdr ["LegacyNumberofpointrecords"] =          0
        hdr ["LegacyNumberofpointsbyreturn"] =        [0,0,0,0]
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
        hdr ["NumberofExtendedVariableLengthRecords"] =       0
        hdr ["Numberofpointrecords"] =                        0
        hdr ["Numberofpointsbyreturn"] =                      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

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
        hdr ["LegacyNumberofpointsbyreturn"] =        s[19:23]
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
        hdr ["Numberofpointsbyreturn"] =                      s[40:55]

        self.Xscalefactor = hdr['Xscalefactor']
        self.Yscalefactor = hdr['Yscalefactor']
        self.Zscalefactor = hdr['Zscalefactor']
        self.Xoffset = hdr['Xoffset']
        self.Yoffset = hdr['Yoffset']
        self.Zoffset = hdr['Zoffset']

        hdrList = hdr.values()
        h = tuple(hdrList)

        self.hdr = hdr
    
###############################################################################
class laswriter:
    def __init__(self, filename):
        self.fileName = filename
        self.fileptr = open(filename, 'wb')        
        self.hdr = lashdr()

    def writeHeader():

        # convert the header variables into a list, then conver the list into a tuple so we can pack it
        hdrList = hdr.values()
        values = tuple(hdrList)
        s = struct.Struct(self.hdrfmt)
        data = struct.pack(*values)
        self.fileptr.write(data)

        # values = (1, 'ab', 2.7)
        # s = struct.Struct('I 2s f')
        # packed_data = s.pack(*values)


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
        data = self.fileptr.read(self.ptfmt1len * recordsToRead)
        result = []
        i = 0
        for r in range(recordsToRead):
            j = i+self.ptfmt1len
            result.append(struct.unpack(self.ptfmt1, data[i:j]))
            i = j
        return result

    def readpointrecord(self, recordsToRead=1):
        if self.PointDataRecordFormat == 1:
                
            ptfmt = "<lllHBBbBHd"
            ptlen = struct.calcsize(ptfmt)
            data = self.fileptr.read(ptlen)
            s = struct.unpack(ptfmt, data)

            self.X                   = s[0]
            self.Y                   = s[1]
            self.Z                   = s[2]
            self.Intensity           = s[3]
            self.ReturnNumber        = s[4]
            self.NumberofReturns     = s[4]
            self.ScanDirectionFlag   = s[4]
            self.EdgeOfFlight        = s[4]
            self.Classification      = s[5]
            self.ScanAngleRank       = s[6]
            self.UserData            = s[7]
            self.PointSourceID       = s[8]
            self.GPSTime             = s[9]

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


if __name__ == "__main__":
        main()

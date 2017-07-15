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
# import sys


def main():
    #open the ALL file for reading by creating a new ALLReader class and passin in the filename to open.
    # filename =   "C:/Python27/ArcGIS10.3/pyall-master/em2000-0017-e_007-20111101-093632.all"
    # filename =   "C:/development/Python/m3Sample.all"
    filename = "C:/development/python/sample.las"
    r = lasreader(filename)
    r.readhdr()
    print (r)

    for i in range(r.NumberofVariableLengthRecords):
        r.readvariablelengthrecord()

    # now find the start point for the point records
    r.seekPoints()
    for i in range(r.Numberofpointrecords):
        r.readpointrecord()

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

    def seekPoints(self):
        # go back to start of file
        self.fileptr.seek(self.Offsettopointdata, 0)                

    def __str__(self):
        return pprint.pformat(vars(self))

    def readpointrecord(self):
        if self.PointDataRecordFormat == 1:
                
            ptfmt = "<3lHBBbBHd"
            ptlen = struct.calcsize(ptfmt)
            data = self.fileptr.read(ptlen)
            s = struct.unpack(ptfmt, data)

            self.X                   = s[0]
            self.Y                   = s[1]
            self.Y                   = s[2]
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

    def readhdr(self):

        hdrfmt = "<4sHHLHH8sBB32s32sHHHLLBHL5LddddddddddddQQLQ15Q"
        hdrlen = struct.calcsize(hdrfmt)

        # curr = self.fileptr.tell()
        data = self.fileptr.read(hdrlen)
        s = struct.unpack(hdrfmt, data)

        self.FileSignature                      = s[0]
        self.FileSourceID                       = s[1]
        self.GlobalEncoding                     = s[2]
        self.ProjectIDGUIDdata1                 = s[3]
        self.ProjectIDGUIDdata2                 = s[4]
        self.ProjectIDGUIDdata3                 = s[5]
        self.ProjectIDGUIDdata4                 = s[6]
        self.VersionMajor                       = s[7]
        self.VersionMinor                       = s[8]
        self.SystemIdentifier                   = s[9]
        self.GeneratingSoftware                 = s[10]
        self.FileCreationDayofYear              = s[11]
        self.FileCreationYear                   = s[12]
        self.HeaderSize                         = s[13]
        self.Offsettopointdata                  = s[14]
        self.NumberofVariableLengthRecords      = s[15]
        self.PointDataRecordFormat              = s[16]
        self.PointDataRecordLength              = s[17]
        self.LegacyNumberofpointrecords         = s[18]
        self.LegacyNumberofpointsbyreturn       = s[19:23]
        self.Xscalefactor                       = s[24]
        self.Yscalefactor                       = s[25]
        self.Zscalefactor                       = s[26]
        self.Xoffset                            = s[27]
        self.Yoffset                            = s[28]
        self.Zoffset                            = s[29]
        self.MaxX                               = s[30]
        self.MinX                               = s[31]
        self.MaxY                               = s[32]
        self.MinY                               = s[33]
        self.MaxZ                               = s[34]
        self.MinZ                               = s[35]
        self.StartofWaveformDataPacketRecord    = s[36]
        self.StartoffirstExtendedVariableLengthRecord   = s[37]
        self.NumberofExtendedVariableLengthRecords      = s[38]
        self.Numberofpointrecords                       = s[39]
        self.Numberofpointsbyreturn                     = s[40:55]

if __name__ == "__main__":
        main()

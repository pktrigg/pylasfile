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
import math
import random

def main():

    testreader()
    testwriter()

def testwriter():
    '''
    sample write script so we can see how to use the code
    '''
    outFileName = os.path.join(os.path.dirname(os.path.abspath("c:/development/python/laswriter.las")), "laswriter.las")
    outFileName = createOutputFileName(outFileName)
    print("outputfile %s" % outFileName)
    writer = laswriter(outFileName)
    writer.writeHeader()

    # now write some points
    writer.hdr.PointDataRecordFormat = 1
    pointslist = []
    for _ in range(1000):
        writer.x.append(round(random.uniform(1, 50000000),6))
        writer.y.append(round(random.uniform(1, 100000),6))
        writer.z.append(round(random.uniform(1, 1000),6))

        
    start_time = time.time() # time the process so we can keep it quick

    # before we write any piints, we need to compute the bounding box, scale and offsets
    writer.computebbox_offsets(pointslist)
    writer.writepoints()
    # writer.writepoints(pointslist)

    # we need to write the header after writing records so we can update the bounding box, point format etc 
    writer.writeHeader()
    writer.close()

    print("Write duration %.3fs" % (time.time() - start_time )) # time the process

###############################################################################
class laswriter:
    def __init__(self, filename):
        self.fileName = filename
        self.fileptr = open(filename, 'wb')        
        self.hdr = lashdr()

        # the lists of all the data we will populate, then write into whatever format the user desires.  
        # these could be numpy arrays, but that introduces a dependency, so we will leave them as lists
        self.x = []
        self.y = []
        self.z = []
        self.intensity = []
        self.returnnumber = []
        self.numberreturns = []
        self.scandirectionflag = []
        self.edgeflightline = []
        self.classification = []
        self.scananglerank = []
        self.userdata = []
        self.pointsourceid = []
        self.gpstime = []
        self.red = []
        self.green = []
        self.blue = []
        self.wavepacketdescriptorindex = []
        self.byteoffsettowaveformdata = []
        self.waveformpacketsize = []
        self.returnpointwaveformlocation = []
        self.wavex = []
        self.wavey = []
        self.wavez = []
        self.nir = []

        self.classificationflags = []
        self.scannerchannel = []
        self.userdata = []
        self.scanangle = []

        self.supportedformats = self.hdr.getsupportedformats()

    def getsupportedformats():
        s = []
        # format 0
        fmt = "<lllHBBbBH"
        fmtlen = struct.calcsize(fmt)
        s.append[fmt,fmtlen]

        # format 1
        fmt = "<lllHBBbBHd"
        fmtlen = struct.calcsize(fmt)
        s.append[fmt,fmtlen]
        return s

        # format 2
        fmt = "<lllHBBbBHd"
        fmtlen = struct.calcsize(fmt)
        s.append[fmt,fmtlen]
        return s


    def computebbox_offsets(self, records):
        '''
        compute the bounding box of all records in the list
        '''

        self.hdr.MaxX = max(self.x) 
        self.hdr.MinX = min(self.x) 

        self.hdr.MaxY = max(self.y) 
        self.hdr.MinY = min(self.y)

        self.hdr.MaxZ = max(self.z) 
        self.hdr.MinZ = min(self.z) 

        self.hdr.Xoffset = self.hdr.MinX 
        self.hdr.Yoffset = self.hdr.MinY
        self.hdr.Zoffset = self.hdr.MinZ

        # compute the scale factor based on the maximal number of decimal places in the first and last records.
        # digit1, afterDP1 = self.precision_and_scale(self.hdr.MaxX)
        # digit2, afterDP2 = self.precision_and_scale(self.hdr.MinX)
        # self.hdr.Xscalefactor = 10**-(max(afterDP1, afterDP2)-max(digit1,digit2))

        digit2, afterDP2 = self.precision_and_scale(self.hdr.MaxX - self.hdr.MinX)
        self.hdr.Xscalefactor = 10**-(8-digit2)

        digit2, afterDP2 = self.precision_and_scale(self.hdr.MaxY - self.hdr.MinY)
        self.hdr.Yscalefactor = 10**-(8-digit2)

        digit2, afterDP2 = self.precision_and_scale(self.hdr.MaxZ - self.hdr.MinZ)
        self.hdr.Zscalefactor = 10**-(8-digit2)

        # digit1, afterDP1 = self.precision_and_scale(self.hdr.MaxY)
        # digit2, afterDP2 = self.precision_and_scale(self.hdr.MinY)
        # self.hdr.Yscalefactor = 10**-(max(afterDP1, afterDP2)-max(digit1,digit2))

        # digit1, afterDP1 = self.precision_and_scale(self.hdr.MaxZ)
        # digit2, afterDP2 = self.precision_and_scale(self.hdr.MinZ)
        # self.hdr.Zscalefactor = 10**-(max(afterDP1, afterDP2)-max(digit1,digit2))

        # set the z scale to cm resolution
        # self.hdr.Zscalefactor = 0.01

    def precision_and_scale(self, x):
        max_digits = 14
        int_part = int(abs(x))
        magnitude = 1 if int_part == 0 else int(math.log10(int_part)) + 1
        if magnitude >= max_digits:
            return (magnitude, 0)
        frac_part = abs(x) - int_part
        multiplier = 10 ** (max_digits - magnitude)
        frac_digits = multiplier + int(multiplier * frac_part + 0.5)
        while frac_digits % 10 == 0:
            frac_digits /= 10
        scale = int(math.log10(frac_digits))
        return (magnitude, scale)
        # return (scale) #return the number of digits after the decimal point only

    def zerolistmaker(self, n):
        listofzeros = [0] * n
        return listofzeros

    def fixemptylists(self):
        if len(self.intensity) == 0: 
            self.intensity = self.zerolistmaker(len(self.x))
        if len(self.returnnumber) == 0:
            self.returnnumber = self.zerolistmaker(len(self.x))
        if len(self.numberreturns) == 0: 
            self.numberreturns = self.zerolistmaker(len(self.x))
        if len(self.scandirectionflag) == 0: 
            self.scandirectionflag = self.zerolistmaker(len(self.x))
        if len(self.edgeflightline) == 0: 
            self.edgeflightline = self.zerolistmaker(len(self.x))
        if len(self.classification) == 0: 
            self.classification = self.zerolistmaker(len(self.x))
        if len(self.scananglerank) == 0: 
            self.scananglerank = self.zerolistmaker(len(self.x))
        if len(self.userdata) == 0: 
            self.userdata = self.zerolistmaker(len(self.x))
        if len(self.pointsourceid) == 0: 
            self.pointsourceid = self.zerolistmaker(len(self.x))
        if len(self.gpstime) == 0: 
            self.gpstime = self.zerolistmaker(len(self.x))
        if len(self.red) == 0: 
            self.red = self.zerolistmaker(len(self.x))
        if len(self.green) == 0: 
            self.green = self.zerolistmaker(len(self.x))
        if len(self.blue) == 0: 
            self.blue = self.zerolistmaker(len(self.x))
        if len(self.wavepacketdescriptorindex) == 0: 
            self.wavepacketdescriptorindex = self.zerolistmaker(len(self.x))
        if len(self.byteoffsettowaveformdata) == 0: 
            self.byteoffsettowaveformdata = self.zerolistmaker(len(self.x))
        if len(self.waveformpacketsize) == 0: 
            self.waveformpacketsize = self.zerolistmaker(len(self.x))
        if len(self.returnpointwaveformlocation) == 0: 
            self.returnpointwaveformlocation = self.zerolistmaker(len(self.x))
        if len(self.wavex) == 0: 
            self.wavex = self.zerolistmaker(len(self.x))
        if len(self.wavey) == 0: 
            self.wavey = self.zerolistmaker(len(self.x))
        if len(self.wavez) == 0: 
            self.wavez = self.zerolistmaker(len(self.x))
        if len(self.nir) == 0: 
            self.nir = self.zerolistmaker(len(self.x))

        if len(self.classificationflags) == 0:
            self.classificationflags = self.zerolistmaker(len(self.x))
        if len(self.scannerchannel) == 0:
            self.scannerchannel = self.zerolistmaker(len(self.x))
        if len(self.userdata) == 0:
            self.userdata = self.zerolistmaker(len(self.x))
        if len(self.scanangle) == 0:
            self.scanangle = self.zerolistmaker(len(self.x))

    def writepoints(self):
        xs = self.hdr.Xscalefactor
        ys = self.hdr.Yscalefactor
        zs = self.hdr.Zscalefactor

        xo = self.hdr.Xoffset
        yo = self.hdr.Yoffset
        zo = self.hdr.Zoffset
    
        self.fixemptylists()

        self.hdr.Numberofpointrecords += len(self.x)
        self.hdr.LegacyNumberofpointrecords += len(self.x)

        if self.hdr.PointDataRecordFormat == 0:
            for i in range(len(self.x)):
                flags = setpointflags(self.returnnumber[i], self.numberreturns[i], self.scandirectionflag[i], self.edgeflightline[i])
                n = (int((self.x[i] - xo) / xs),
                    int((self.y [i] - yo) / ys),
                    int((self.z [i] - zo) / zs),
                    int(self.intensity[i]),
                    flags,
                    self.classification[i],
                    self.scanangle[i],
                    self.userdata[i],
                    self.pointsourceid[i]
                    )
                # now write the record to disc
                record_struct = struct.Struct(self.supportedformats[self.hdr.PointDataRecordFormat][0])
                self.fileptr.write(record_struct.pack(*n))

        if self.hdr.PointDataRecordFormat == 1:
            for i in range(len(self.x)):
                flags = self.setpointflags(self.returnnumber[i], self.numberreturns[i], self.scandirectionflag[i], self.edgeflightline[i])
                n = (int((self.x[i] - xo) / xs),
                    int((self.y [i] - yo) / ys),
                    int((self.z [i] - zo) / zs),
                    int(self.intensity[i]),
                    flags,
                    self.classification[i],
                    self.scanangle[i],
                    self.userdata[i],
                    self.pointsourceid[i],
                    self.gpstime[i]
                    )
                # now write the record to disc
                record_struct = struct.Struct(self.supportedformats[self.hdr.PointDataRecordFormat][0])
                self.fileptr.write(record_struct.pack(*n))

        if self.hdr.PointDataRecordFormat == 2:
    # def makepoint2(self, x, y, z, intensity=0, returnnumber=0, numberreturns=0, scandirectionflag=0, edgeflightline=0, classification=0, scananglerank=0, userdata=0, pointsourceid=0, red=255, green=255, blue=255):
    #     return (x, y, z, intensity, returnnumber, numberreturns, scandirectionflag, edgeflightline, classification, scananglerank, userdata, pointsourceid, red, green, blue)
            for i in range(len(self.x)):
                flags = self.setpointflags(self.returnnumber[i], self.numberreturns[i], self.scandirectionflag[i], self.edgeflightline[i])
                n = (int((self.x[i] - xo) / xs),
                    int((self.y [i] - yo) / ys),
                    int((self.z [i] - zo) / zs),
                    int(self.intensity[i]),
                    flags,
                    self.classification[i],
                    self.scanangle[i],
                    self.userdata[i],
                    self.pointsourceid[i],
                    self.red[i],
                    self.green[i],
                    self.blue[i]
                    
                    )
                # now write the record to disc
                record_struct = struct.Struct(self.supportedformats[self.hdr.PointDataRecordFormat][0])
                self.fileptr.write(record_struct.pack(*n))


        if self.hdr.PointDataRecordFormat == 3:
    # def makepoint3(self, x, y, z, intensity=0, returnnumber=0, numberreturns=0, scandirectionflag=0, edgeflightline=0, classification=0, scananglerank=0, userdata=0, pointsourceid=0, gpstime=0, red=255, green=255, blue=255):
    #     return (x, y, z, intensity, returnnumber, numberreturns, scandirectionflag, edgeflightline, classification, scananglerank, userdata, pointsourceid, gpstime, red, green, blue)
            for i in range(len(self.x)):
                flags = self.setpointflags(self.returnnumber[i], self.numberreturns[i], self.scandirectionflag[i], self.edgeflightline[i])
                n = (int((self.x[i] - xo) / xs),
                    int((self.y [i] - yo) / ys),
                    int((self.z [i] - zo) / zs),
                    int(self.intensity[i]),
                    flags,
                    self.classification[i],
                    self.scanangle[i],
                    self.userdata[i],
                    self.pointsourceid[i],
                    self.gpstime[i],
                    self.red[i],
                    self.green[i],
                    self.blue[i]
                    )
                # now write the record to disc
                record_struct = struct.Struct(self.supportedformats[self.hdr.PointDataRecordFormat][0])
                self.fileptr.write(record_struct.pack(*n))

        if self.hdr.PointDataRecordFormat == 4:
    # def makepoint4(self, x, y, z, intensity=0, returnnumber=0, numberreturns=0, scandirectionflag=0, edgeflightline=0, classification=0, scananglerank=0, userdata=0, pointsourceid=0, gpstime=0, wavepacketdescriptorindex=0, byteoffsettowaveformdata=0, waveformpacketsize=0, returnpointwaveformlocation=0, waveX=0, waveY=0, waveZ=0):
    #     return (x, y, z, intensity, returnnumber, numberreturns, scandirectionflag, edgeflightline, classification, scananglerank, userdata, pointsourceid, gpstime, wavepacketdescriptorindex, byteoffsettowaveformdata, waveformpacketsize, returnpointwaveformlocation, waveX, waveY, waveZ)
            for i in range(len(self.x)):
                flags = self.setpointflags(self.returnnumber[i], self.numberreturns[i], self.scandirectionflag[i], self.edgeflightline[i])
                n = (int((self.x[i] - xo) / xs),
                    int((self.y [i] - yo) / ys),
                    int((self.z [i] - zo) / zs),
                    int(self.intensity[i]),
                    flags,
                    self.classification[i],
                    self.scanangle[i],
                    self.userdata[i],
                    self.pointsourceid[i],
                    self.gpstime[i],
                    self.wavepacketdescriptorindex[i],
                    self.byteoffsettowaveformdata[i],
                    self.waveformpacketsize[i],
                    self.returnpointwaveformlocation[i],
                    self.waveX[i],
                    self.waveY[i],
                    self.waveZ[i]
                    )
                # now write the record to disc
                record_struct = struct.Struct(self.supportedformats[self.hdr.PointDataRecordFormat][0])
                self.fileptr.write(record_struct.pack(*n))


        if self.hdr.PointDataRecordFormat == 5:
    # def makepoint5(self, x, y, z, intensity=0, returnnumber=0, numberreturns=0, scandirectionflag=0, edgeflightline=0, classification=0, scananglerank=0, userdata=0, pointsourceid=0, gpstime=0, red=255, green=255, blue=255, wavepacketdescriptorindex=0, byteoffsettowaveformdata=0, waveformpacketsize=0, returnpointwaveformlocation=0, waveX=0, waveY=0, waveZ=0):
    #     return (x, y, z, intensity, returnnumber, numberreturns, scandirectionflag, edgeflightline, classification, scananglerank, userdata, pointsourceid, gpstime, red, green, blue, wavepacketdescriptorindex, byteoffsettowaveformdata, waveformpacketsize, returnpointwaveformlocation, waveX, waveY, waveZ)
            for i in range(len(self.x)):
                flags = self.setpointflags(self.returnnumber[i], self.numberreturns[i], self.scandirectionflag[i], self.edgeflightline[i])
                n = (int((self.x[i] - xo) / xs),
                    int((self.y [i] - yo) / ys),
                    int((self.z [i] - zo) / zs),
                    int(self.intensity[i]),
                    flags,
                    self.classification[i],
                    self.scanangle[i],
                    self.userdata[i],
                    self.pointsourceid[i],
                    self.gpstime[i],
                    self.red[i],
                    self.green[i],
                    self.blue[i],
                    self.wavepacketdescriptorindex[i],
                    self.byteoffsettowaveformdata[i],
                    self.waveformpacketsize[i],
                    self.returnpointwaveformlocation[i],
                    self.waveX[i],
                    self.waveY[i],
                    self.waveZ[i]
                    )
                # now write the record to disc
                record_struct = struct.Struct(self.supportedformats[self.hdr.PointDataRecordFormat][0])
                self.fileptr.write(record_struct.pack(*n))


        if self.hdr.PointDataRecordFormat == 6:
    # def makepoint6(self, x, y, z, intensity=0, returnnumber=0, numberreturns=0, classificationflags=0, scannerchannel=0, scandirectionflag=0, edgeflightline=0, classification=0, userdata=0, scanangle=0, pointsourceid=0, gpstime=0):
    #     return (x, y, z, intensity, returnnumber, numberreturns, classificationflags, scannerchannel, scandirectionflag, edgeflightline, classification, userdata, scanangle, pointsourceid, gpstime)
            for i in range(len(self.x)):
                flags = self.setpointflags(self.returnnumber[i], self.numberreturns[i], self.scandirectionflag[i], self.edgeflightline[i])
                n = (int((self.x[i] - xo) / xs),
                    int((self.y [i] - yo) / ys),
                    int((self.z [i] - zo) / zs),
                    int(self.intensity[i]),
                    flags,
                    self.classification[i],
                    self.scanangle[i],
                    self.userdata[i],
                    self.pointsourceid[i],
                    self.gpstime[i]
                    )
                # now write the record to disc
                record_struct = struct.Struct(self.supportedformats[self.hdr.PointDataRecordFormat][0])
                self.fileptr.write(record_struct.pack(*n))

        if self.hdr.PointDataRecordFormat == 7:
    # def makepoint7(self, x, y, z, intensity=0, returnnumber=0, numberreturns=0, classificationflags=0, scannerchannel=0, scandirectionflag=0, edgeflightline=0, classification=0, userdata=0, scanangle=0, pointsourceid=0, gpstime=0, red=255, green=255, blue=255):
    #     return (x, y, z, intensity, returnnumber, numberreturns, classificationflags, scannerchannel, scandirectionflag, edgeflightline, classification, userdata, scanangle, pointsourceid, gpstime, red, green, blue)
            for i in range(len(self.x)):
                flags = self.setpointflags(self.returnnumber[i], self.numberreturns[i], self.scandirectionflag[i], self.edgeflightline[i])
                n = (int((self.x[i] - xo) / xs),
                    int((self.y [i] - yo) / ys),
                    int((self.z [i] - zo) / zs),
                    int(self.intensity[i]),
                    flags,
                    self.classification[i],
                    self.scanangle[i],
                    self.userdata[i],
                    self.pointsourceid[i],
                    self.gpstime[i],
                    self.red[i],
                    self.green[i],
                    self.blue[i]
                    )
                # now write the record to disc
                record_struct = struct.Struct(self.supportedformats[self.hdr.PointDataRecordFormat][0])
                self.fileptr.write(record_struct.pack(*n))

        if self.hdr.PointDataRecordFormat == 8:
    # def makepoint8(self, x, y, z, intensity=0, returnnumber=0, numberreturns=0, classificationflags=0, scannerchannel=0, scandirectionflag=0, edgeflightline=0, classification=0, userdata=0, scanangle=0, pointsourceid=0, gpstime=0, red=255, green=255, blue=255, nir=0):
    #     return (x, y, z, intensity, returnnumber, numberreturns, classificationflags, scannerchannel, scandirectionflag, edgeflightline, classification, userdata, scanangle, pointsourceid, gpstime, red, green, blue, nir)
            for i in range(len(self.x)):
                flags = self.setpointflags(self.returnnumber[i], self.numberreturns[i], self.scandirectionflag[i], self.edgeflightline[i])
                n = (int((self.x[i] - xo) / xs),
                    int((self.y [i] - yo) / ys),
                    int((self.z [i] - zo) / zs),
                    int(self.intensity[i]),
                    flags,
                    self.classification[i],
                    self.scanangle[i],
                    self.userdata[i],
                    self.pointsourceid[i],
                    self.gpstime[i],
                    self.red[i],
                    self.green[i],
                    self.blue[i],
                    self.nir[i]
                    )
                # now write the record to disc
                record_struct = struct.Struct(self.supportedformats[self.hdr.PointDataRecordFormat][0])
                self.fileptr.write(record_struct.pack(*n))

        if self.hdr.PointDataRecordFormat == 9:
    # def makepoint9(self, x, y, z, intensity=0, returnnumber=0, numberreturns=0, classificationflags=0, scannerchannel=0, scandirectionflag=0, edgeflightline=0, classification=0, userdata=0, scanangle=0, pointsourceid=0, gpstime=0, wavepacketdescriptorindex=0, byteoffsettowaveformdata=0, waveformpacketsize=0, returnpointwaveformlocation=0, waveX=0, waveY=0, waveZ=0):
    #     return (x, y, z, intensity, returnnumber, numberreturns, classificationflags, scannerchannel, scandirectionflag, edgeflightline, classification, userdata, scanangle, pointsourceid, gpstime, wavepacketdescriptorindex, byteoffsettowaveformdata, waveformpacketsize, returnpointwaveformlocation, waveX, waveY, waveZ)
            for i in range(len(self.x)):
                flags = self.setpointflags(self.returnnumber[i], self.numberreturns[i], self.scandirectionflag[i], self.edgeflightline[i])
                n = (int((self.x[i] - xo) / xs),
                    int((self.y [i] - yo) / ys),
                    int((self.z [i] - zo) / zs),
                    int(self.intensity[i]),
                    flags,
                    self.classification[i],
                    self.userdata[i],
                    self.scanangle[i],
                    self.pointsourceid[i],
                    self.gpstime[i],
                    self.red[i],
                    self.green[i],
                    self.blue[i],
                    self.wavepacketdescriptorindex[i],
                    self.byteoffsettowaveformdata[i],
                    self.waveformpacketsize[i],
                    self.returnpointwaveformlocation[i],
                    self.waveX[i],
                    self.waveY[i],
                    self.waveZ[i]
                    )
                # now write the record to disc
                record_struct = struct.Struct(self.supportedformats[self.hdr.PointDataRecordFormat][0])
                self.fileptr.write(record_struct.pack(*n))

        if self.hdr.PointDataRecordFormat == 10:
    # def makepoint10(self, x, y, z, intensity=0, returnnumber=0, numberreturns=0, classificationflags=0, scannerchannel=0, scandirectionflag=0, edgeflightline=0, classification=0, userdata=0, scanangle=0, pointsourceid=0, gpstime=0, red=255, green=255, blue=255, nir=0, wavepacketdescriptorindex=0, byteoffsettowaveformdata=0, waveformpacketsize=0, returnpointwaveformlocation=0, waveX=0, waveY=0, waveZ=0):
    #     return (x, y, z, intensity, returnnumber, numberreturns, classificationflags, scannerchannel, scandirectionflag, edgeflightline, classification, userdata, scanangle, pointsourceid, gpstime, red, green, blue, nir, wavepacketdescriptorindex, byteoffsettowaveformdata, waveformpacketsize, returnpointwaveformlocation, waveX, waveY, waveZ)
            for i in range(len(self.x)):
                flags = self.setpointflags(self.returnnumber[i], self.numberreturns[i], self.scandirectionflag[i], self.edgeflightline[i])
                n = (int((self.x[i] - xo) / xs),
                    int((self.y [i] - yo) / ys),
                    int((self.z [i] - zo) / zs),
                    int(self.intensity[i]),
                    flags,
                    self.classification[i],
                    self.userdata[i],
                    self.scanangle[i],
                    self.pointsourceid[i],
                    self.gpstime[i],
                    self.red[i],
                    self.green[i],
                    self.blue[i],
                    self.wavepacketdescriptorindex[i],
                    self.byteoffsettowaveformdata[i],
                    self.waveformpacketsize[i],
                    self.returnpointwaveformlocation[i],
                    self.waveX[i],
                    self.waveY[i],
                    self.waveZ[i]
                    )
                # now write the record to disc
                record_struct = struct.Struct(self.supportedformats[self.hdr.PointDataRecordFormat][0])
                self.fileptr.write(record_struct.pack(*n))

    def close(self):
        self.fileptr.close()
        
    def rewind(self):
        # go back to start of file
        self.fileptr.seek(0, 0)                

    def seekPointRecordStart(self):
        # set the file pointer to the start of the points block
        self.fileptr.seek(self.hdr.Offsettopointdata, 0)                

    def seekPointRecordEnd(self):
        # set the file pointer to the start of the points block
        self.fileptr.seek(self.hdr.Offsettopointdata + (self.hdr.Numberofpointrecords * self.hdr.PointDataRecordLength), 0)

    def writeHeader(self):
        # convert the header variables into a list, then conver the list into a tuple so we can pack it
        values = self.hdr.hdr2tuple()
        # values = tuple(hdrList)
        s = struct.Struct(self.hdr.hdrfmt)
        data = s.pack(*values)
        self.fileptr.seek(0, 0)                
        self.fileptr.write(data)


    def setpointflags(self, returnnumber, numberreturns, scandirectionflag, edgeflightline ):
        flags = 0
        flags = self.setBitsFor_returnNo(flags, returnnumber)
        flags = self.setBitsFor_numberreturns(flags, numberreturns)
        flags = self.setBitsFor_scandirectionflag(flags, scandirectionflag)
        flags = self.setBitsFor_edgeflightline(flags, edgeflightline)
        return flags

    def setpointflags_6_10(self, returnnumber, numberreturns, classificationflags, scannerchannel, scandirectionflag, edgeflightline ):
        flags = 0
        flags = self.setBitsFor_returnNo6_10(flags, returnnumber)
        flags = self.setBitsFor_numberreturns6_10(flags, numberreturns)
        flags = self.setBitsFor_scandirectionflag(flags, scandirectionflag)
        flags = self.setBitsFor_edgeflightline(flags, edgeflightline)
        return flags

    def isBitSet(self, int_type, offset):
        '''testBit() returns a nonzero result, 2**offset, if the bit at 'offset' is one.'''
        mask = 1 << offset
        return (int_type & (1 << offset)) != 0

    def bitSet(self, v, offset):
        '''
        Set the index:th bit of v to 1 if x is truthy, else to 0, and return the new value.
        '''
        mask = 1 << offset   # Compute mask, an integer with just bit 'index' set.
        #   v &= ~mask          # Clear the bit indicated by the mask (if x is False)
        #   if x:
        v |= mask         # If x was True, set the bit indicated by the mask.
        return v            # Return the result, we're done.

    def setBitsFor_edgeflightline(self, int_type, edgeflightline):
        if edgeflightline: # set the bit if this is the edge of a scan
            int_type = bitSet(int_type, 7)
        return int_type

    def setBitsFor_scandirectionflag(self, int_type, scandirectionflag):
        if scandirectionflag: #positive direction
            int_type = bitSet(int_type, 6)
        return int_type

    def setBitsFor_numberreturns(self, int_type, numberreturns):
        if numberreturns == 0:
            return int_type
        if numberreturns == 1:
            int_type = bitSet(int_type, 3)
            return int_type
        if numberreturns == 2:
            int_type = bitSet(int_type, 4)
            return int_type
        if numberreturns == 3:
            int_type = bitSet(int_type, 3)
            int_type = bitSet(int_type, 4)
            return int_type
        if numberreturns == 4:
            int_type = bitSet(int_type, 5)
            return int_type
        if numberreturns == 5:
            int_type = bitSet(int_type, 3)
            int_type = bitSet(int_type, 5)
            return int_type
        return int_type

    def setBitsFor_returnNo(self, int_type, returnNo):
        if returnNo == 0:
            return int_type
        if returnNo == 1:
            int_type = bitSet(int_type, 0)
            return int_type
        if returnNo == 2:
            int_type = bitSet(int_type, 1)
            return int_type
        if returnNo == 3:
            int_type = bitSet(int_type, 0)
            int_type = bitSet(int_type, 1)
            return int_type
        if returnNo == 4:
            int_type = bitSet(int_type, 2)
            return int_type
        if returnNo == 5:
            int_type = bitSet(int_type, 0)
            int_type = bitSet(int_type, 2)
            return int_type
        return int_type

    def setBitsFor_returnNo6_10(self, int_type, returnNo):
        # bits 0-3
        if returnNo == 0:
            return int_type
        if returnNo == 1:
            int_type = bitSet(int_type, 0)
            return int_type
        if returnNo == 2:
            int_type = bitSet(int_type, 1)
        if returnNo == 3:
            int_type = bitSet(int_type, 0)
            int_type = bitSet(int_type, 1)
            return int_type
        if returnNo == 4:
            int_type = bitSet(int_type, 2)
            return int_type
        if returnNo == 5:
            int_type = bitSet(int_type, 0)
            int_type = bitSet(int_type, 2)
            return int_type
        if returnNo == 6:
            int_type = bitSet(int_type, 1)
            int_type = bitSet(int_type, 2)
            return int_type
        if returnNo == 7:
            int_type = bitSet(int_type, 0)
            int_type = bitSet(int_type, 1)
            int_type = bitSet(int_type, 2)
            return int_type
        if returnNo == 8:
            int_type = bitSet(int_type, 3)
            return int_type
        if returnNo == 9:
            int_type = bitSet(int_type, 0)
            int_type = bitSet(int_type, 3)
            return int_type
        if returnNo == 10:
            int_type = bitSet(int_type, 1)
            int_type = bitSet(int_type, 3)
            return int_type
        if returnNo == 11:
            int_type = bitSet(int_type, 0)
            int_type = bitSet(int_type, 1)
            int_type = bitSet(int_type, 3)
            return int_type
        if returnNo == 12:
            int_type = bitSet(int_type, 2)
            int_type = bitSet(int_type, 3)
            return int_type
        if returnNo == 13:
            int_type = bitSet(int_type, 0)
            int_type = bitSet(int_type, 2)
            int_type = bitSet(int_type, 3)
            return int_type
        if returnNo == 14:
            int_type = bitSet(int_type, 1)
            int_type = bitSet(int_type, 2)
            int_type = bitSet(int_type, 3)
            return int_type
        if returnNo == 15:
            int_type = bitSet(int_type, 0)
            int_type = bitSet(int_type, 1)
            int_type = bitSet(int_type, 2)
            int_type = bitSet(int_type, 3)
            return int_type
        return int_type

    def setBitsFor_numberreturns6_10(self, int_type, numberreturns):
        # bits 4-7
        if numberreturns == 0:
            return int_type
        if numberreturns == 1:
            int_type = bitSet(int_type, 4)
            return int_type
        if numberreturns == 2:
            int_type = bitSet(int_type, 5)
            return int_type
        if numberreturns == 3:
            int_type = bitSet(int_type, 4)
            int_type = bitSet(int_type, 5)
            return int_type
        if numberreturns == 4:
            int_type = bitSet(int_type, 6)
            return int_type
        if numberreturns == 5:
            int_type = bitSet(int_type, 4)
            int_type = bitSet(int_type, 6)
            return int_type
        if numberreturns == 6:
            int_type = bitSet(int_type, 5)
            int_type = bitSet(int_type, 6)
            return int_type
        if numberreturns == 7:
            int_type = bitSet(int_type, 4)
            int_type = bitSet(int_type, 5)
            int_type = bitSet(int_type, 6)
            return int_type
        if numberreturns == 8:
            int_type = bitSet(int_type, 8)
            return int_type
        if numberreturns == 9:
            int_type = bitSet(int_type, 4)
            int_type = bitSet(int_type, 8)
            return int_type
        if numberreturns == 10:
            int_type = bitSet(int_type, 5)
            int_type = bitSet(int_type, 7)
            return int_type
        if numberreturns == 11:
            int_type = bitSet(int_type, 4)
            int_type = bitSet(int_type, 6)
            int_type = bitSet(int_type, 7)
            return int_type
        if numberreturns == 12:
            int_type = bitSet(int_type, 6)
            int_type = bitSet(int_type, 7)
            return int_type
        if numberreturns == 13:
            int_type = bitSet(int_type, 4)
            int_type = bitSet(int_type, 6)
            int_type = bitSet(int_type, 7)
            return int_type
        if numberreturns == 14:
            int_type = bitSet(int_type, 5)
            int_type = bitSet(int_type, 6)
            int_type = bitSet(int_type, 7)
            return int_type
        if numberreturns == 15:
            int_type = bitSet(int_type, 4)
            int_type = bitSet(int_type, 5)
            int_type = bitSet(int_type, 6)
            int_type = bitSet(int_type, 7)
            return int_type
        return int_type

    def setBitsFor_classificationflags6_10(self, int_type, classificationflags):
        # bits 0-3
        if classificationflags == 0:
            return int_type
        if classificationflags == 1:
            int_type = bitSet(int_type, 0)
            return int_type
        if classificationflags == 2:
            int_type = bitSet(int_type, 1)
        if classificationflags == 3:
            int_type = bitSet(int_type, 0)
            int_type = bitSet(int_type, 1)
            return int_type
        if classificationflags == 4:
            int_type = bitSet(int_type, 2)
            return int_type
        if classificationflags == 5:
            int_type = bitSet(int_type, 0)
            int_type = bitSet(int_type, 2)
            return int_type
        if classificationflags == 6:
            int_type = bitSet(int_type, 1)
            int_type = bitSet(int_type, 2)
            return int_type
        if classificationflags == 7:
            int_type = bitSet(int_type, 0)
            int_type = bitSet(int_type, 1)
            int_type = bitSet(int_type, 2)
            return int_type
        if classificationflags == 8:
            int_type = bitSet(int_type, 3)
            return int_type
        if classificationflags == 9:
            int_type = bitSet(int_type, 0)
            int_type = bitSet(int_type, 3)
            return int_type
        if classificationflags == 10:
            int_type = bitSet(int_type, 1)
            int_type = bitSet(int_type, 3)
            return int_type
        if classificationflags == 11:
            int_type = bitSet(int_type, 0)
            int_type = bitSet(int_type, 1)
            int_type = bitSet(int_type, 3)
            return int_type
        if classificationflags == 12:
            int_type = bitSet(int_type, 2)
            int_type = bitSet(int_type, 3)
            return int_type
        if classificationflags == 13:
            int_type = bitSet(int_type, 0)
            int_type = bitSet(int_type, 2)
            int_type = bitSet(int_type, 3)
            return int_type
        if classificationflags == 14:
            int_type = bitSet(int_type, 1)
            int_type = bitSet(int_type, 2)
            int_type = bitSet(int_type, 3)
            return int_type
        if classificationflags == 15:
            int_type = bitSet(int_type, 0)
            int_type = bitSet(int_type, 1)
            int_type = bitSet(int_type, 2)
            int_type = bitSet(int_type, 3)
            return int_type
        return int_type

    def setBitsFor_scannerchannel6_10(self, int_type, scannerchannel):
        # bits 4 & 5
        if scannerchannel == 0:
            return int_type
        if scannerchannel == 1:
            int_type = bitSet(int_type, 4)
            return int_type
        if scannerchannel == 2:
            int_type = bitSet(int_type, 5)
            return int_type
        if scannerchannel == 3:
            int_type = bitSet(int_type, 4)
            int_type = bitSet(int_type, 5)
            return int_type
        return int_type

###############################################################################
class lashdr:
    def __init__(self):

        # version 1.4 header format
        self.hdrfmt = "<4sHHL HH8sBB 32s32sHHH LLBHL 5Ldddd ddddd dddQQ LQ15Q"
        self.hdrlen = struct.calcsize(self.hdrfmt)

        # create a default template for a V1.4 header.  We use this for writing purposes
        # hdr = OrderedDict()
        self.FileSignature =                       b'LASF'
        self.FileSourceID  =                       0
        self.GlobalEncoding =                      17
        self.ProjectIDGUIDdata1 =                  0
        self.ProjectIDGUIDdata2 =                  0
        self.ProjectIDGUIDdata3 =                  0
        self.ProjectIDGUIDdata4 =                  b"12345678"
        self.VersionMajor =                        1
        self.VersionMinor =                        4

        self.SystemIdentifier =                    b'pylasfile writer'
        self.GeneratingSoftware =                  b'pylasfile writer'
        self.FileCreationDayofYear =               datetime.datetime.now().timetuple().tm_yday
        self.FileCreationYear =                    datetime.datetime.now().year
        self.HeaderSize =                          375
        self.Offsettopointdata =                   375
        self.NumberofVariableLengthRecords =       0
        self.PointDataRecordFormat =               1
        self.PointDataRecordLength =               28

        self.LegacyNumberofpointrecords =          0
        self.LegacyNumberofpointsbyreturn1 =       0
        self.LegacyNumberofpointsbyreturn2 =       0
        self.LegacyNumberofpointsbyreturn3 =       0
        self.LegacyNumberofpointsbyreturn4 =       0
        self.LegacyNumberofpointsbyreturn5 =       0
        self.Xscalefactor =                        1
        self.Yscalefactor =                        1
        self.Zscalefactor =                        1

        self.Xoffset =                             0
        self.Yoffset =                             0
        self.Zoffset =                             0
        self.MaxX =                                -9999999999 #make the default the extreme opposite, so we compute real values along the way
        self.MinX =                                9999999999
        self.MaxY =                                -9999999999
        self.MinY =                                9999999999
        self.MaxZ =                                -9999999999
        self.MinZ =                                9999999999

        self.StartofWaveformDataPacketRecord =     0
        self.StartoffirstExtendedVariableLengthRecord =    0
        self.NumberofExtendedVariableLengthRecords   = 0
        self.Numberofpointrecords =                0
        self.Numberofpointsbyreturn1 =             0  
        self.Numberofpointsbyreturn2 =             0  
        self.Numberofpointsbyreturn3 =             0  
        self.Numberofpointsbyreturn4 =             0  
        self.Numberofpointsbyreturn5 =             0  

        self.Numberofpointsbyreturn6 =             0  
        self.Numberofpointsbyreturn7 =             0  
        self.Numberofpointsbyreturn8 =             0  
        self.Numberofpointsbyreturn9 =             0  
        self.Numberofpointsbyreturn10 =             0  
        self.Numberofpointsbyreturn11 =             0  
        self.Numberofpointsbyreturn12 =             0  
        self.Numberofpointsbyreturn13 =             0  
        self.Numberofpointsbyreturn14 =             0  
        self.Numberofpointsbyreturn15 =             0  

    def __str__(self):
        '''
        pretty print this class
        '''
        return pprint.pformat(vars(self))

    def hdr2tuple(self):
        '''
        convert the header properties into a tuple so we can easily write it to disc using struct
        '''    
        return (
                self.FileSignature, 
                self.FileSourceID,
                self.GlobalEncoding,
                self.ProjectIDGUIDdata1,
                self.ProjectIDGUIDdata2, 
                self.ProjectIDGUIDdata3, 
                self.ProjectIDGUIDdata4,
                self.VersionMajor,
                self.VersionMinor,

                self.SystemIdentifier,
                self.GeneratingSoftware,
                self.FileCreationDayofYear,
                self.FileCreationYear,
                self.HeaderSize,
                self.Offsettopointdata,
                self.NumberofVariableLengthRecords,
                self.PointDataRecordFormat,
                self.PointDataRecordLength,

                self.LegacyNumberofpointrecords,
                self.LegacyNumberofpointsbyreturn1,
                self.LegacyNumberofpointsbyreturn2,
                self.LegacyNumberofpointsbyreturn3,
                self.LegacyNumberofpointsbyreturn4,
                self.LegacyNumberofpointsbyreturn5,
                self.Xscalefactor,
                self.Yscalefactor,
                self.Zscalefactor,

                self.Xoffset,
                self.Yoffset,
                self.Zoffset,
                self.MaxX,
                self.MinX,
                self.MaxY,
                self.MinY,
                self.MaxZ,
                self.MinZ,

                self.StartofWaveformDataPacketRecord,
                self.StartoffirstExtendedVariableLengthRecord,
                self.NumberofExtendedVariableLengthRecords,
                self.Numberofpointrecords,
                self.Numberofpointsbyreturn1,  
                self.Numberofpointsbyreturn2,  
                self.Numberofpointsbyreturn3,  
                self.Numberofpointsbyreturn4,  
                self.Numberofpointsbyreturn5,  

                self.Numberofpointsbyreturn6,  
                self.Numberofpointsbyreturn7,  
                self.Numberofpointsbyreturn8,  
                self.Numberofpointsbyreturn9,  
                self.Numberofpointsbyreturn10,  
                self.Numberofpointsbyreturn11,  
                self.Numberofpointsbyreturn12,  
                self.Numberofpointsbyreturn13,  
                self.Numberofpointsbyreturn14,  
                self.Numberofpointsbyreturn15,  
                )

    def decodehdr(self, data):
        '''
        decode a header from a bytearray
        '''
        s = struct.unpack(self.hdrfmt, data)

        self.FileSignature =                        s[0]
        self.FileSourceID =                         s[1]
        self.GlobalEncoding =                      s[2]
        self.ProjectIDGUIDdata1 =                  s[3]
        self.ProjectIDGUIDdata2 =                  s[4]
        self.ProjectIDGUIDdata3 =                  s[5]
        self.ProjectIDGUIDdata4 =                  s[6]
        self.VersionMajor =                        s[7]
        self.VersionMinor =                        s[8]

        self.SystemIdentifier =                    s[9]
        self.GeneratingSoftware =                  s[10]
        self.FileCreationDayofYear =               s[11]
        self.FileCreationYear =                    s[12]
        self.HeaderSize =                          s[13]
        self.Offsettopointdata =                   s[14]
        self.NumberofVariableLengthRecords =       s[15]
        self.PointDataRecordFormat =               s[16]
        self.PointDataRecordLength =               s[17]

        self.LegacyNumberofpointrecords =          s[18]
        self.LegacyNumberofpointsbyreturn1 =       s[19]
        self.LegacyNumberofpointsbyreturn2 =       s[20]
        self.LegacyNumberofpointsbyreturn3 =       s[21]
        self.LegacyNumberofpointsbyreturn4 =       s[22]
        self.LegacyNumberofpointsbyreturn5 =       s[23]
        self.Xscalefactor =                        s[24]
        self.Yscalefactor =                        s[25]
        self.Zscalefactor =                        s[26]
        self.Xoffset =                             s[27]

        self.Yoffset =                             s[28]
        self.Zoffset =                             s[29]
        self.MaxX =                                s[30]
        self.MinX =                                s[31]
        self.MaxY =                                s[32]
        self.MinY =                                s[33]
        self.MaxZ =                                s[34]
        self.MinZ =                                s[35]

        self.StartofWaveformDataPacketRecord =     s[36]
        self.StartoffirstExtendedVariableLengthRecord =    s[37]
        self.NumberofExtendedVariableLengthRecords =       s[38]
        self.Numberofpointrecords =                        s[39]
        self.Numberofpointsbyreturn1 =                     s[40]
        self.Numberofpointsbyreturn2 =                     s[41]
        self.Numberofpointsbyreturn3 =                     s[42]
        self.Numberofpointsbyreturn4 =                     s[43]
        self.Numberofpointsbyreturn5 =                     s[44]

        self.Numberofpointsbyreturn6 =                     s[45]
        self.Numberofpointsbyreturn7 =                     s[46]
        self.Numberofpointsbyreturn8 =                     s[47]
        self.Numberofpointsbyreturn9 =                     s[48]
        self.Numberofpointsbyreturn10 =                    s[49]
        self.Numberofpointsbyreturn11 =                    s[50]
        self.Numberofpointsbyreturn12 =                    s[51]
        self.Numberofpointsbyreturn13 =                    s[52]
        self.Numberofpointsbyreturn14 =                    s[53]
        self.Numberofpointsbyreturn15 =                    s[54]

    def getsupportedformats(self):
        '''
        compose a list o the supported point file formats, so we can easily find them
        '''
        s = []
        # format 0
        fmt = "<lllHBBbBH"
        fmtlen = struct.calcsize(fmt)
        s.append([fmt,fmtlen])

        # format 1
        fmt = "<lllHBBbBHd"
        fmtlen = struct.calcsize(fmt)
        s.append([fmt,fmtlen])

        # format 2
        fmt = "<lllHBBbBH HHH"
        fmtlen = struct.calcsize(fmt)
        s.append([fmt,fmtlen])

        return s

    def get_PointDataRecordFormat(self):
        return self._PointDataRecordFormat

    def set_PointDataRecordFormat(self, value):
        self._PointDataRecordFormat = value
        self.PointDataRecordLength = self.getsupportedformats()[value][1]

    PointDataRecordFormat = property(get_PointDataRecordFormat,set_PointDataRecordFormat)

###############################################################################
class lasreader:
    def __init__(self, filename):
        if not os.path.isfile(filename):
            print ("file not found:", filename)
        self.fileName = filename
        self.fileptr = open(filename, 'rb')        
        self.fileSize = os.path.getsize(filename)
        self.hdr = lashdr()
        self.supportedformats = self.hdr.getsupportedformats()

        # the lists of all the data we will populate, then write into whatever format the user desires.  
        # these could be numpy arrays, but that introduces a dependency, so we will leave them as lists
        self.x = []
        self.y = []
        self.z = []
        self.intensity = []
        self.returnnumber = []
        self.numberreturns = []
        self.scandirectionflag = []
        self.edgeflightline = []
        self.classification = []
        self.scananglerank = []
        self.userdata = []
        self.pointsourceid = []
        self.gpstime = []
        self.red = []
        self.green = []
        self.blue = []
        self.wavepacketdescriptorindex = []
        self.byteoffsettowaveformdata = []
        self.waveformpacketsize = []
        self.returnpointwaveformlocation = []
        self.wavex = []
        self.wavey = []
        self.wavez = []
        self.nir = []

        self.classificationflags = []
        self.scannerchannel = []
        self.userdata = []
        self.scanangle = []


    def close(self):
        '''
        close the file
        '''
        self.fileptr.close()
        
    def rewind(self):
        '''
        go back to start of file
        '''
        self.fileptr.seek(0, 0)                

    def seekPointRecordStart(self):
        '''
        set the file pointer to the START of the points block so we can write some records
        '''
        self.fileptr.seek(self.hdr.Offsettopointdata, 0)                

    def seekPointRecordEnd(self):
        '''
        set the file pointer to the END of the points block so we can add new records
        '''
        self.fileptr.seek(self.hdr.Offsettopointdata + (self.hdr.Numberofpointrecords*self.hdr.PointDataRecordLength), 0)

    def __str__(self):
        '''
        pretty print this class
        '''
        return pprint.pformat(vars(self))

    def readhdr(self):
        '''
        read the las file header from disc
        '''
        data = self.fileptr.read(self.hdr.hdrlen)
        self.hdr.decodehdr(data)

    def unpackpoints(self, records):
        '''
        the points read into the list need unpacking into the real world useful data
        '''
        for r in records:
            self.x.append((r[0] * self.hdr.Xscalefactor) + self.hdr.Xoffset)
            self.y.append((r[1] * self.hdr.Yscalefactor) + self.hdr.Yoffset)
            self.z.append((r[2] * self.hdr.Zscalefactor) + self.hdr.Zoffset)

    def readpointrecords(self, recordsToRead=1):
        '''
        read the required number of records from the file
        '''
        data = self.fileptr.read(self.supportedformats[self.hdr.PointDataRecordFormat][1] * recordsToRead)
        result = []
        i = 0
        for r in range(recordsToRead):
            j = i + self.supportedformats[self.hdr.PointDataRecordFormat][1]
            result.append(struct.unpack(self.supportedformats[self.hdr.PointDataRecordFormat][0], data[i:j]))
            i = j
        
        return result

    def readvariablelengthrecord(self):
        '''
        read a variable length record from the file
        '''
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


def testreader():
    '''
    sample read script so we can see how to use the code
    '''
    start_time = time.time() # time the process so we can keep it quick

    filename = "C:/development/python/sample.las"
    # filename = "C:/development/python/version1.4_format0.las"
    # create a lasreader class and pass the filename
    r = lasreader(filename)
    # r.read the header
    r.readhdr()

    # print some metadata about the reader
    print (r.hdr)

    # read the variable records
    for i in range(r.hdr.NumberofVariableLengthRecords):
        r.readvariablelengthrecord()

    # now find the start point for the point records
    r.seekPointRecordStart()
    # read the point data
    points = r.readpointrecords(64)
    # points = r.readpointrecords(r.hdr.Numberofpointrecords)
    
    # unpack from the native formmat into lists so we can do something with them
    r.unpackpoints(points)

    # for i in range(len(r.x)):
    #     print ("%.3f, %.3f %.3f" % (r.x[i], r.y[i], r.z[i]))
        
    # for p in points:
    #     print ("%.3f, %.3f %.3f" % ((p[0] * r.hdr.Xscalefactor) + r.hdr.Xoffset, (p[1] * r.hdr.Yscalefactor) + r.hdr.Yoffset, (p[2] * r.hdr.Zscalefactor) + r.hdr.Zoffset))

    print("Duration %.3fs" % (time.time() - start_time )) # time the process

    return

def isBitSet(int_type, offset):
    '''testBit() returns a nonzero result, 2**offset, if the bit at 'offset' is one.'''
    mask = 1 << offset
    return (int_type & (1 << offset)) != 0


###############################################################################
if __name__ == "__main__":
        main()


















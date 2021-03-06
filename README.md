# pylasfile
python native las read/write module.

This is going to use the standard libraries from python, ie NOT use numpy, liblas, or external any dependencies.

# 2DO
* add support for lazzip so we can unzip and zip
* add support for extended VLR
* try out mmap to see if it is quicker

# DONE
* tested writer in all formats with lasinfo.
* add write support for v1.2
* add read support for las 1.2 (for support of fm)
* add test for 'LASF' in header, and quit if invalid
* add test for header byte read so we can see what version las to read
* add VLR for WGS84 CRS
* code clean up
* Implement writer and confirm it is a valid file
* implement bit fields on point objects
* implement computation of scale and offset for data. geogs should be 0.0000001, grid should be 0.001
* implemented format 0
* moved header into bespoke class
* Can read 2.9 million points in 2.4 seconds on my laptop, ie about a million points per second.  
* Points 'format 1' reads correclty
* VLR reads correctly
* Header reads correctly
* Implemented reading of header into a dictionary
* Implemented reading of variable length records
* Implemented reading of n points into a list
* Basic reader for LAS V1.4


## Public Header Block
```
FileSignature (“LASF”) char[4] 4 bytes                          4s
FileSourceID unsigned short 2 bytes                             H
GlobalEncoding unsigned short 2 bytes                           H
ProjectIDGUIDdata1 unsigned long 4 bytes                        L
ProjectIDGUIDdata2 unsigned short 2 byte                        H
ProjectIDGUIDdata3 unsigned short 2 byte                        H
ProjectIDGUIDdata4 unsigned char[8] 8 bytes                     8B
VersionMajor unsigned char 1 byte *                             B
VersionMinor unsigned char 1 byte *                             B
SystemIdentifier char[32] 32 bytes *                            32c
GeneratingSoftware char[32] 32 bytes *                          32c
FileCreationDayofYear unsigned short 2 bytes *                  32c
FileCreationYear unsigned short 2 bytes *                       H
HeaderSize unsigned short 2 bytes *                             H
Offsettopointdata unsigned long 4 bytes *                       L
NumberofVariableLengthRecords unsigned long 4 bytes *           L
PointDataRecordFormat unsigned char 1 byte *                    B
PointDataRecordLength unsigned short 2 bytes *                  H
LegacyNumberofpointrecords unsigned long 4 bytes *              L
LegacyNumberofpoints by return unsigned long [5] 20 bytes *     5L
Xscalefactor double 8 bytes *                                   d 
Yscalefactor double 8 bytes *                                   d 
Zscalefactor double 8 bytes *                                   d  
Xoffset double 8 bytes *                                        d
Yoffset double 8 bytes *                                        d
Zoffset double 8 bytes *                                        d
MaxX double 8 bytes *                                           d
MinX double 8 bytes *                                           d
MaxY double 8 bytes *                                           d
MinY double 8 bytes *                                           d
MaxZ double 8 bytes *                                           d
MinZ double 8 bytes *                                           d
StartofWaveformDataPacketRecord Unsigned long long 8 bytes *    Q
StartoffirstExtendedVariableLengthRecord unsigned long long 8 bytes *   Q
NumberofExtendedVariableLengthRecords unsigned long 4 bytes *           L
Numberofpointrecords unsigned long long 8 bytes *                       Q
Numberofpointsbyreturn unsigned long long [15] 120 bytes                15Q
```
  
## Python Struct format characters
```
Format	C Type	            Python type	            Standard size	    
x	    pad byte	        no value	 	 
c	    char	            string of length 1	    1	 
b	    signed char	        integer	                1	
B	    unsigned char	    integer	                1	
?	    _Bool	            bool	                1	
h	    short	            integer	                2
H	    unsigned short	    integer	                2	
i	    int	                integer	                4	
I	    unsigned int	    integer	                4	
l	    long	            integer	                4	
L	    unsigned long	    integer	                4	
q	    long long	        integer 	            8
Q	    unsigned long long	integer	                8
f	    float	            float               	4
d	    double	            float               	8
s	    char[]	            string	 	 
p	    char[]	            string	 	 
P	    void *	            integer	 	
import numpy as np
import time
from PIL import Image

from laspy.file import File

start_time = time.time() # time the process so we can keep it quick
inFile = File("c:/development/python/sample.las", mode = "r")

# Grab all of the points from the file.
point_records = inFile.points

data = np.histogram2d(inFile.get_x(), inFile.get_y(), weights = inFile.get_z())
img = Image.fromarray(data)
img.show()


print ("%d" % len(inFile))
print("read duration %.3fs" % (time.time() - start_time )) # time the process

# img.save('my.png')
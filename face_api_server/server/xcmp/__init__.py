import xcmp_file
import sys
print >>sys.stderr, dir(xcmp_file)
print >>sys.stderr, xcmp_file.__file__
xcmp = xcmp_file.xcmp_fun
print >>sys.stderr, "xcmp is " , xcmp

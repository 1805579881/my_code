
#!/usr/bin/python
#!-*-coding:UTF8-*-
import numpy

import ctypes

score = numpy.ones(5, 'f');
idx = numpy.ones(5, 'l');

for i in score:
    print(i,type(i))


for i in idx:
    print(i,type(i))
#!/usr/bin/python
#!-*-coding:UTF8-*-
import xcmp_cpp
import numpy
def xcmp_fun(feature, db_name, top = 5, threshold = 0.2):
    n_of_top = min(10, top);
    score = numpy.ones(n_of_top, 'f');
    idx = numpy.ones(n_of_top, 'l');
    # 转为float32类型
    feature = numpy.array(feature, dtype="float32")
    xcmp_cpp.xcmp(feature,  db_name, score, idx)
    return [(i, c) for c, i  in zip(score.tolist(), idx.tolist()) if c > threshold]

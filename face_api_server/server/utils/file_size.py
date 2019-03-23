#!/usr/bin/python
#!-*-coding:UTF8-*-
import os
from base_response import BaseResponse

def get_file_size(image):
    try:
        file_size = len(image.read())
        file_size = float(file_size)
        file_size_Mb = file_size / 1024
        return file_size_Mb
    except Exception as e:
       raise e

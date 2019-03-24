#!/usr/bin/python
#!-*-coding:UTF8-*-
import os
from base_response import BaseResponse


def get_file_size(image):
    try:
        image_bytes = image.read()
        file_size = len(image_bytes)
        file_size = float(file_size)
        file_size_Mb = file_size / 1024
        return file_size_Mb,image_bytes
    except Exception as e:
       raise e

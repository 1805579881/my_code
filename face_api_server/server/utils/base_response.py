#!/usr/bin/python
#!-*-coding:UTF8-*-


class BaseResponse():
    """
        返回的数据格式
    """

    def __init__(self):
        self.data = None
        self.code = 1000
        self.message = ""

    @property
    def dict(self):
        return self.__dict__




















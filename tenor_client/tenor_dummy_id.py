#!/usr/bin/python
# -*- coding: utf-8 -*-

class TenorDummyId(object):
    """Manages mixed ids ... ints for vnfs and unicode for nsd"""
    def __init__(self, value):
        self._id = value

    def __add__(self, other):
        if type(self._id) is int:
            return str(self._id+other)
        elif type(self._id) is unicode:
            number = int(self._id)
            return str(number+1).decode('unicode-escape')

    def __repr__(self):
        return str(self._id)

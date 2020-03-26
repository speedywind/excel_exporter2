#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

_isdebug = False


def set_debug_mode(value):
    global _isdebug
    _isdebug = value


def info(*vals):
    if len(vals) > 1:
        print(vals)
    else:
        print(vals[0])

def debug(*vals):
    if _isdebug:
        if len(vals) > 1:
            print(vals)
        else:
            print(vals[0])

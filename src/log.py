#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

_isdebug = False


def set_debug_mode(value):
    global _isdebug
    _isdebug = value


def debug(vals):
    if _isdebug:
        print(vals)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import os
import re
import json
from .log import debug
from .config import config

check_config = None

imglacks = {}
TFileTag = "watergun"
TDefault = "default"
TInt = "int"
TBool = "bool"
TFloat = "float"
TString = "string"
TStruct = "struct"
TList = "list"
TNextLevel = "<"
myrow = 1
mycol = 0
filename = "watergun"
sheetname = "watergun"


def is_localize(txt):
    for localize2, flag2 in config['localize'].items():
        if txt and txt.find(localize2) >= 0:
            return True
    return False


def MatchInList(l, name):
    for e in l:
        if re.match(e, name):
            return True
    return False


def IsMyInt0(name):
    return MatchInList(check_config['IsMyInt0'], name)


def IsMyInt(name):
    return MatchInList(check_config['IsMyInt'], name)


def IsMyString(name):
    return MatchInList(check_config['IsMyString'], name)


def IsMyFloat(name):
    return MatchInList(check_config['IsMyFloat'], name)


def IsMyStruct(name):
    return MatchInList(check_config['IsMyStruct'], name)


class Parse():
    def __init__(self):
        self.default = None
        self.args = None
        self.func = None
        self.name = None

    def __repr__(self):
        return "Parse(default='%s', args=%s, func='%s', name='%s')" % (self.default, self.args, self.func, self.name)


def CheckParses(fields):
    parses = []
    while len(fields) > 0:
        # debug(fields)
        field = fields.pop(0)
        if not field:
            parse = Parse()
            parses.append(parse)
            continue
        if TNextLevel == field[:len(TNextLevel)]:  # 父子
            field = field[len(TNextLevel):]
            for index, val in enumerate(fields):
                if TNextLevel == val[:len(TNextLevel)]:
                    fields[index] = val[len(TNextLevel):]
        if TFileTag == field[:len(TFileTag)]:
            field = field[field.find(":") + 1:]
        parse = Parse()
        typepos = field.rfind(":")
        fieldtype = field[:typepos]
        name = field[typepos + 1:]
        valuepos = name.rfind("=")
        if valuepos != -1:  # 设置默认值
            parse.default = name[valuepos + 1:]
            name = name[:valuepos]
        parse.name = name
        # debug(fieldtype, name, parse)
        if TDefault == fieldtype[:len(TDefault)]:  # 默认字段,只出现在list和struct中
            parse.func = TDefault
        elif TInt == fieldtype[:len(TInt)]:
            parse.func = TInt
        elif TBool == fieldtype[:len(TBool)]:
            parse.func = TBool
        elif TFloat == fieldtype[:len(TFloat)]:
            parse.func = TFloat
        elif TString == fieldtype[:len(TString)]:
            parse.func = TString
            if parse.default and parse.default != "key" and parse.default[:1] != "\"" and parse.default[-1:] != "\"":
                parse.default = CheckString(parse.default)
        elif typepos == -1 and IsMyInt0(name):
            fieldtype = TInt
            parse.func = TInt
            if parse.default == None:
                parse.default = "0"
        elif typepos == -1 and IsMyInt(name):
            fieldtype = TInt
            parse.func = TInt
        elif typepos == -1 and IsMyFloat(name):
            fieldtype = TFloat
            parse.func = TFloat
            if parse.default == None:
                parse.default = "0"
        elif typepos == -1 and IsMyString(name):
            fieldtype = TString
            parse.func = TString
            if parse.default and parse.default != "key" and parse.default[:1] != "\"" and parse.default[-1:] != "\"":
                parse.default = CheckString(parse.default)
        else:
            if TList == fieldtype[:len(TList)]:
                parse.func = TList
                nextfield = fieldtype[len(TList) + 1:-1]
                nextfields = IsMyStruct(nextfield) and [nextfield + ":"] or ["struct<" + nextfield + ">:"]
                debug(nextfields)
            elif TStruct == fieldtype[:len(TStruct)]:
                parse.func = TStruct
                nextfields = fieldtype[len(TStruct) + 1:-1].split(",")
            elif IsMyStruct(fieldtype):
                parse.func = TStruct
                nextfields = CheckMyStruct(fieldtype, fields)
            else:
                assert field == None, "Error[非法的字段名]: near " + \
                    field + "\n" + str(parses)
            endpos = len(fields)
            for m in range(0, endpos):
                if len(fields[m]) != 0 and TInt != fields[m][:len(TInt)] and TBool != fields[m][:len(TBool)] \
                        and TFloat != fields[m][:len(TFloat)] and TString != fields[m][:len(TString)] and TNextLevel != fields[m][:len(TNextLevel)] \
                        and not IsMyInt0(fields[m].split('=')[0]) and not IsMyFloat(fields[m].split('=')[0]) and not IsMyInt(fields[m].split('=')[0]) and not IsMyString(fields[m].split('=')[0]):
                    endpos = m
                    debug(endpos, fields[endpos])
                    break
            # debug(endpos, nextfields + fields[0:endpos])
            assert TList != fieldtype[:len(TList)] or endpos == 0 or fields[endpos - 1] == None or IsMyStruct(
                nextfields[0]), "Error[list后请不要配一级字段]: near " + field + "\n" + str(parses)
            parse.args = CheckParses(nextfields + fields[:endpos])
            parse1 = parse.args.pop()
            if parse1.func == TStruct:
                parse.args.append(parse1)
                parse2 = parse1.args.pop()
                if parse2.func == TList and parse.name == parse2.name:  # 父子合并
                    # if parse.args != parse2.args:
                    # 	debug("Warning "+)
                    parse.args += parse2.args
                else:
                    parse1.args.append(parse2)
            elif parse1.func == TList and parse.name == parse1.name:
             # and parse.args == parse1.args: #父子合并
                parse.args += parse1.args
            else:
                parse.args.append(parse1)
            # debug(parse)
            fields = fields[endpos:]
        if len(parses) > 0:
            debug(parses[len(parses)-1]," += ",parse)
        if len(parses) > 0 and parse.func == TList and parse.name == parses[len(parses) - 1].name:
            # and (parse.args == parses[len(parses)-1].args or (type(parses[len(parses)-1].args) is list \
            # and parse.args == parses[len(parses)-1].args[:1])): #同级合并
            parse.args = parses[len(parses) - 1].args + parse.args
            parses.pop()
        for index, parse1 in enumerate(parses):
            assert parse.name != parse1.name, "Error[重复的字段]: near " + \
                field + "\n" + str(parses)
        parses.append(parse)
    debug(parses)
    return parses


def ValToKey(val):
    # return val
    return val.isdecimal() and "[" + val + "]" or val


def CheckMyStruct(fieldtype, fields):
    if fieldtype[:len("reward")] == "reward":
        nextfields = fieldtype[len("reward") + 1:-1].split(",")
        for parse in (nextfields + fields):
            if TList == parse[:len(TList)] or TStruct == parse[:len(TStruct)] or IsMyStruct(parse) or TNextLevel == parse[:len(TNextLevel)]:
                break
            assert parse.find("itemid") in [0, len("string:"), len("default:")]\
                or parse.find("count") in [0, len("int:"), len("float:"), len("default:")]\
                or parse.find("rate") in [0, len("int:"), len("default:")]\
                or parse.find("weight") in [0, len("int:"), len("float:"), len("default:")] or not parse,\
                "Error[非法的数据结构]: near " + fieldtype + \
                "\n" + str(nextfields + fields)
    else:
        assert not fieldtype, "Error[未识别的数据结构]: near " + fieldtype
    return nextfields


number_pattern = re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$')
int_pattern = re.compile(r'^[-+]?[-0-9]\d*$')


def CheckInt(data, args=None):
    if data == None:
        assert args != "key", "Error[主键不能为空]: near " + sheetname + \
            filename + "(" + GetColNum(mycol) + str(myrow + 1) + ")"
        assert args != None, "Error[字段不能为空]: near " + sheetname + \
            filename + "(" + GetColNum(mycol) + str(myrow + 1) + ")"
        return args
    assert int_pattern.match(data), "Error[非法的整型]: found {} near {} {} ({}{})".format(
        data, sheetname, filename, GetColNum(mycol), str(myrow))
    return data


def CheckBool(data, args=None):
    if data == None:
        assert args, "Error[字段不能为空]: near " + sheetname +\
            filename + "(" + GetColNum(mycol) + str(myrow + 1) + ")"
        return "False" if args == 'false' else "True"
    return ('0' == data or 'false' == data) and "False" or "True"


def CheckFloat(data, args=None):
    if data == None:
        assert args, "Error[字段不能为空]: near " + sheetname +\
            filename + "(" + GetColNum(mycol) + str(myrow + 1) + ")"
        return args
    assert number_pattern.match(data), "Error[非法的浮点型]: found {} near {} {} ({}{})".format(
        data, sheetname, filename, GetColNum(mycol), str(myrow))
    return data


def CheckString(data, args=None):
    if data == None:
        if args == None:
            return "\"\""
        else:
            return args
    if isinstance(data, str):
        data = data.replace("\n", "\\n")
        data = data.replace('"', r'\"')
    else:
        data = str(data)
    return '"' + data + '"'


def GetValue(sheet, row, col):
    return sheet.cell(row, col)


def GetType(name):
    if name[0] == 'i':
        return "int"
    elif name[0] == 'b':
        return "bool"
    elif name[0] == 'f':
        return "float"
    elif name[0] == 's':
        return "string"


def getColByName(parses, name):
    col1 = 0
    result = False
    for parse in parses:
        if parse.name == name:
            return col1, True
        elif parse.func == TDefault:
            continue
        elif parse.func == TStruct:
            col, result = getColByName(parse.args, name)
            col1 += col
        elif parse.func == TList:
            col, result = getColByName(parse.args, name)
            col1 += col
        else:  # 跳过空字段或基础字段
            col1 += 1
        if result:
            return col1, True
    return col1, result


def changeBase(n, b):
    x, y = divmod(n, b)
    return changeBase(x-1, b) + chr(y+65) if x > 0 else chr(y+65)


def GetColNum(col):
    return changeBase(col-1, 26)


def GetCols(parses):
    func_count = 0
    for p in parses:
        if p.func not in [TDefault, TList, TStruct]:
            func_count += 1
        if p.args:
            func_count += GetCols(p.args)
    return func_count


def CheckChunk(parses, sheet, row1, row2, col):
    global sheetname
    global filename
    global myrow
    global mycol
    global imglacks
    sheetname = sheet.title
    filename = GetValue(sheet, 1, 1)
    pychunks = []
    while row1 < row2:
        myrow = row1
        col1 = col
        pychunk = []
        majorkey = None
        newrow2 = GetNextRow(sheet, row1 + 1, row2, col)
        debug("parse (" + str(row1) + "-" + str(newrow2) + "," + str(col)+")")
        for parse in parses:
            mycol = col1
            if parse == None:
                col1 += 1
                continue
            field = parse.func == TDefault and parse.default or GetValue(sheet, row1, col1)
            key = parse.name
            debug(myrow, mycol, parse.func, key, field)
            if parse.func == TDefault:
                assert parse.default, "Error[无效的默认值]: near " + sheetname + \
                    filename + "(" + GetColNum(mycol) + str(myrow + 1) + ")"
                pychunk.append("\"" + key + "\":" + parse.default)
                continue
            elif parse.func == TInt:
                val = CheckInt(field, parse.default)
                pychunk.append(key and "\"" + key + "\":" + val or val)
                if parse.default == "key":
                    assert not majorkey, "Error[重复的主键]: near " + sheetname + \
                        filename + "(" + GetColNum(mycol) + \
                        str(myrow + 1) + ")"
                    majorkey = "" + str(val) + ""
                col1 += 1
            elif parse.func == TBool:
                value = CheckBool(field, parse.default)
                pychunk.append("\"" + key + "\":" + value if key else value)
                col1 += 1
            elif parse.func == TFloat:
                value = CheckFloat(field, parse.default)
                pychunk.append(key and "\"" + key + "\":" + value or value)
                col1 += 1
            elif parse.func == TString:
                val = CheckString(field, parse.default)
                if val != '""':
                    pychunk.append(key and "\"" + key +
                                   "\":" + Quotes(val) or Quotes(val))
                if parse.default == "key":
                    assert not majorkey, "Error[重复的主键]: near " + sheetname + \
                        filename + "(" + GetColNum(mycol) + \
                        str(myrow + 1) + ")"
                    majorkey = str(val)
                col1 += 1
            elif parse.func == TStruct:
                if GetValue(sheet, row1, col1) == None and parse.args[0].default == None:
                    col1 += GetCols(parse.args)
                else:
                    newrow2 = GetNextRow(sheet, row1 + 1, newrow2, col1)
                    col1, py, _ = CheckChunk(parse.args, sheet, row1, newrow2, col1)
                    if parse.args[0].default == "key":
                        pychunk.append(py)
                    elif py:
                        pychunk.append(key and "\"" + key +"\":{" + py + "}" or "{" + py + "}")
            elif parse.func == TList:
                col1, py, _ = CheckChunk(parse.args, sheet, row1, newrow2, col1,)
                if parse.args[0].args[0].default == "key":
                    pychunk.append("\"" + key + "\":{" + py + "}")
                else:
                    pychunk.append("\"" + key + "\":[" + py + "]")
            else:  # 跳过空字段
                assert parse.func == None, "Error[非法的字段名]: near " + sheetname + \
                    filename + "(" + GetColNum(mycol) + str(myrow + 1) + ")"
                col1 += 1
            # debug(pychunk[len(pychunk)-1])
        if majorkey:
            if hasattr(parses[0],"localize") and is_localize(majorkey) and majorkey.find(parses[0].localize) >= 0:
                majorkey = majorkey.replace("_" + parses[0].localize, "")
                pychunk[0] = pychunk[0].replace("_" + parses[0].localize, "")
            if not is_localize(majorkey):
                pychunks.append(majorkey + ":{" + ", ".join(pychunk) + "}")
        elif len(pychunk) > 0:  # 列表比如{1,2,3}
            pychunks.append(",".join(pychunk))
        row1 = newrow2
    return col1, ",".join(pychunks), len(pychunks)

def ParseSheet(fields, conf):
    global check_config
    check_config = conf
    return CheckParses(fields)


def ProcessSheet(parses, sheet, row_start):
    _, py, num = CheckChunk(
        parses, sheet, row_start, sheet.max_row, 1)
    return py, num

def PairsHook(lst):
    result={}
    for key,val in lst:
        assert not key in result, "Error[重复的主键]: near " + sheetname + \
                    filename + "(" + key + ")"
        result[key]=val
    return result

def FormatSheet(py):
    py = "{"+py+"}"
    return eval(py)
    # return json.loads(py, object_pairs_hook=PairsHook)


def Quotes(val):
    if val[:1] == '"':
        return val
    return '"' + val + '"'


def GetNextRow(sheet, row1, row2, col):
    for newrow2 in range(row1, row2):
        if GetValue(sheet, newrow2, col) != None:
            return newrow2
    return row2

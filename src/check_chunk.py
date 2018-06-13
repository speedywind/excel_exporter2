#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import os
import time
import re

from log import debug

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


def MatchInList(l, name):
    for e in l:
        if re.match(e, name):
            return True
    return False


def IsMyInt0(name):
    return MatchInList(config['IsMyInt0'], name)


def IsMyInt(name):
    return MatchInList(config['IsMyInt'], name)


def IsMyString(name):
    return MatchInList(config['IsMyString'], name)


def IsMyFloat(name):
    return MatchInList(config['IsMyFloat'], name)


def IsMyStruct(name):
    return MatchInList(config['IsMyStruct'], name)


class Parse():
    def __init__(self):
        self.default = None
        self.args = None
        self.func = None
        self.name = None


def CheckParses(fields):
    result = []
    while len(fields) > 0:
        # print fields
        field = fields.pop(0)
        if not field:
            parse = Parse()
            result.append(parse)
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
        parse.name = ValToKey(name)
        # print fieldtype, name, parse
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
            if parse.default and parse.default[:1] != "\"" and parse.default[-1:] != "\"":
                parse.default = CheckString(parse.default)
        elif typepos == -1 and IsMyInt0(name):
            fieldtype = TInt
            parse.func = TInt
            if not parse.default:
                parse.default = "0"
        elif typepos == -1 and IsMyInt(name):
            fieldtype = TInt
            parse.func = TInt
        elif typepos == -1 and IsMyFloat(name):
            fieldtype = TFloat
            parse.func = TFloat
            if not parse.default:
                parse.default = "0"
        elif typepos == -1 and IsMyString(name):
            fieldtype = TString
            parse.func = TString
            if parse.default and parse.default[:1] != "\"" and parse.default[-1:] != "\"":
                parse.default = CheckString(parse.default)
        else:
            if TList == fieldtype[:len(TList)]:
                parse.func = TList
                nextfield = fieldtype[len(TList) + 1:-1]
                nextfields = IsMyStruct(nextfield) and [
                    nextfield + ":"] or ["struct<" + nextfield + ">:"]
                # print nextfields
            elif TStruct == fieldtype[:len(TStruct)]:
                parse.func = TStruct
                nextfields = fieldtype[len(TStruct) + 1:-1].split(",")
            elif IsMyStruct(fieldtype):
                parse.func = TStruct
                nextfields = CheckMyStruct(fieldtype, fields)
            else:
                print(fieldtype, name, parse)
                assert not field, "Error[非法的字段名]: near " + \
                    field + "\n" + str(result)
            endpos = len(fields)
            for m in range(0, endpos):
                if len(fields[m]) != 0 and TInt != fields[m][:len(TInt)] and TBool != fields[m][:len(TBool)] \
                        and TFloat != fields[m][:len(TFloat)] and TString != fields[m][:len(TString)] and TNextLevel != fields[m][:len(TNextLevel)] \
                        and not IsMyInt0(fields[m].split('=')[0]) and not IsMyFloat(fields[m].split('=')[0]) and not IsMyInt(fields[m].split('=')[0]) and not IsMyString(fields[m].split('=')[0]):
                    endpos = m
                    # print endpos, fields[endpos]
                    break
            # print endpos, nextfields + fields[0:endpos]
            assert TList != fieldtype[:len(TList)] or endpos == 0 or not fields[endpos - 1] or IsMyStruct(
                nextfields[0]), "Error[list后请不要配一级字段]: near " + field + "\n" + str(result)
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
            # print parse
            fields = fields[endpos:]
        # if len(result) > 0:
        # 	print parse," += ",result[len(result)-1]
        if len(result) > 0 and parse.func == TList and parse.name == result[len(result) - 1].name:
            # and (parse.args == result[len(result)-1].args or (type(result[len(result)-1].args) is list \
            # and parse.args == result[len(result)-1].args[:1])): #同级合并
            parse.args += result[len(result) - 1].args
            result.pop()
        for index, parse1 in enumerate(result):
            assert parse.name != parse1.name, "Error[重复的字段]: near " + \
                field + "\n" + str(result)
        result.append(parse)
    # print result
    return result


def ValToKey(val):
    return val.isdecimal() and "[" + val + "]" or val


def CheckMyStruct(fieldtype, fields):
    if fieldtype[:len("reward")] == "reward":
        nextfields = fieldtype[len("reward") + 1:-1].split(",")
        for index, parse in enumerate(nextfields + fields):
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


def CheckInt(data, args=None):
    if len(data) == 0:
        assert args != "key", "Error[主键不能为空]: near " + sheetname + \
            filename + "(" + GetColNum(mycol) + str(myrow + 1) + ")"
        assert args != None, "Error[字段不能为空]: near " + sheetname + \
            filename + "(" + GetColNum(mycol) + str(myrow + 1) + ")"
        return args
    vals = data.split('.')
    assert len(vals) == 2 and vals[1] == "0", "Error[非法的整型]: found {} near {} {} ({}{})".format(
        data, sheetname, filename, GetColNum(mycol), str(myrow + 1))
    return vals[0]


def CheckBool(data, args=None):
    if len(data) == 0:
        assert args, "Error[字段不能为空]: near " + sheetname +\
            filename + "(" + GetColNum(mycol) + str(myrow + 1) + ")"
        return "False" if args == 'false' else "True"
    return ("0.0" == data or 'false' == data) and "False" or "True"


def CheckFloat(data, args=None):
    if len(data) == 0:
        assert args, "Error[字段不能为空]: near " + sheetname +\
            filename + "(" + GetColNum(mycol) + str(myrow + 1) + ")"
        return args
    return data


def CheckString(data, args=None):
    if not data:
        if not args:
            return "\"\""
        else:
            return args
    elif data[-2:] == ".0":
        data = data[:-2]
    return "\"" + data.replace("\n", "\\n") + "\""


def GetValue(sheet, row, col):
    return str(sheet.cell(row, col).value).strip()


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
    return changeBase(col, 26)


def GetCols(parse):
    return str(parse).count('func') - str(parse).count('func\': \'' + TDefault) - str(parse).count('func\': \'' + TList) - str(parse).count('func\': \'' + TStruct)


def CheckChunk(parses, sheet, row1, row2, col, indent):
    global sheetname
    global filename
    global myrow
    global mycol
    global imglacks
    sheetname = sheet.name
    filename = GetValue(sheet, 0, 0)
    pychunks = []
    while row1 < row2:
        myrow = row1
        col1 = col
        pychunk = []
        majorkey = None
        newrow2 = GetNextRow(sheet, row1 + 1, row2, col)
        # print "parse row", row1, newrow2
        for index, parse in enumerate(parses):
            mycol = col1
            field = parse.func == TDefault and parse.default or GetValue(
                sheet, row1, col1)
            key = parse.name
            # print myrow, mycol, parse.func, key, field
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
                if val != "\"\"" and key in ["img", "icon"]:
                    rval = val[1:-1]
                if val != "\"\"" or not key in ["img", "ccbi", "starttime", "endtime"]:
                    pychunk.append(key and "\"" + key +
                                   "\":" + Quotes(val) or Quotes(val))
                if parse.default == '"key"':
                    assert not majorkey, "Error[重复的主键]: near " + sheetname + \
                        filename + "(" + GetColNum(mycol) + \
                        str(myrow + 1) + ")"
                    majorkey = "" + str(val) + ""
                col1 += 1
            elif parse.func == TStruct:
                if not GetValue(sheet, row1, col1) and parse.args[0].default == None:
                    col1 += GetCols(parse.args)
                else:
                    col1, py = CheckChunk(
                        parse.args, sheet, row1, newrow2, col1, indent)
                    if py[len(indent) + 1:len(indent) + 2] == "[":
                        pychunk.append(py)
                    elif py:
                        pychunk.append(key and "\"" + key +
                                       "\":{" + py + "}" or "{" + py + "}")
            elif parse.func == TList:
                col1, py = CheckChunk(
                    parse.args, sheet, row1, newrow2, col1, indent + "  ",)
                if parse.default == "key":
                    key = ValToKey(CheckInt(field))
                pychunk.append("\"" + key + "\":[" + py + "]")
            else:  # 跳过空字段
                assert parse.func == None, "Error[非法的字段名]: near " + sheetname + \
                    filename + "(" + GetColNum(mycol) + str(myrow + 1) + ")"
                col1 += 1
            # print luachunk[len(luachunk)-1]
        if majorkey:
            pychunks.append(majorkey +
                            ":{" + ", ".join(pychunk) + "}")
        elif len(pychunk) > 0:  # 列表比如{1,2,3}
            pychunks.append(",".join(pychunk))
        row1 = newrow2
    return col1, ",".join(pychunks)


def ParseSheet(fields, conf):
    global config
    config = conf
    return CheckParses(fields)


def ProcessSheet(parses, sheet, row_start):
    _, py = CheckChunk(
        parses, sheet, row_start, sheet.nrows, 0, "")
    py = "{"+py+"}"
    return eval(py)


def Quotes(val):
    if val[:1] == '"':
        return val
    return '"' + val + '"'


def GetNextRow(sheet, row1, row2, col):
    for newrow1 in range(row1, row2):
        if len(GetValue(sheet, newrow1, col)) != 0:
            return newrow1
    return row2

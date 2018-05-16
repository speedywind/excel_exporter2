#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import os
import time

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


def IsMyInt0(name):
    '''

    售价相关 具体对应货币由表内容决定
    ├─ price 购买价格
    └─ sell 出售价格
    unlockarea 解锁线索等级
    levelvariation 地图等级变化，影响到地图属性
    jump 事件及对白跳转
    '''
    return name == "attack" \
        or name == "defence" \
        or name == "maxhp" \
        or name == "target" \
        or name == "price" \
        or name == "sell" \
        or name == "islevelup" \
        or name == "eyesee" \
        or name == "skill" \
        or name == "skilllevel" \
        or name == "enemylv" \
        or name == "limit" \
        or name == "unlock" \
        or name == "weapon" \
        or name == "weapontype" \
        or name == "unlockcluelevel" \
        or name == "levelvariation" \
        or name == "jump"


def IsMyInt(name):
    '''

    count 数量
    weight 权重
    counta--countb 道具包上下限
    raidlevel 地图等级
    layer 区间层数

    rare 稀有度-决定颜色「暂无养成内容」
    star 星级

    '''
    return name[-4:] == "type" \
        or name == "targettype" \
        or name[-5:] == "level" \
        or name == "bulletset" \
        or name == "bullet" \
        or name == "watertank" \
        or name == "star" \
        or name == "feature" \
        or name == "role" \
        or name == "count" \
        or name == "weight" \
        or name == "counta" \
        or name == "countb" \
        or name == "rare" \
        or name == "star" \
        or name == "weightall" \
        or name == "interval" \
        or name == "raidlevel" \
        or name == "layer" \
        or name == "exp" \
        or name == "gold" \
        or name == "level" \
        or name == "targetcount" \
        or name == "rank" \
        or name == "rank1" \
        or name == "order" \
        or name == "merlevel" \
        or name == "score" \
        or name == "grade" \
        or name == "position" \
        or name == "skip" \
        or name == "rate" \
        or name == "index"


def IsMyString(name):
    '''
    id watergun项目中所有的id均为string
    trigger 触发器
    ├─ condition 触发条件
    └─ state 触发状态
    时间区间
    ├─ starttime 开始时间
    └─ endtime 结束时间

    manufacturer 厂商-厂商大致决定了武器的攻击趋向：暴击伤害类、吸血类、移速类等等
    '''
    return name[-2:] == "id" \
        or name == "condition" \
        or name == "state" \
        or name == "starttime" \
        or name == "endtime" \
        or name == "num" \
        or name == "name" \
        or name[-4:] == "desc" \
        or name == "ccbi" \
        or name == "content" \
        or name == "img" \
        or name == "manufacturer"


def IsMyFloat(name):
    '''
    watertankrecover 水箱回复
    critrate 暴击
    criteffect 暴击伤害
    bulletlife 子弹生命周期
    movespeed 移动速度
    speed 子弹速度
    attackspeed 攻速
    '''
    return name == "watertankrecover" \
        or name == "critrate" \
        or name == "criteffect" \
        or name == "bulletlife" \
        or name == "movespeed" \
        or name == "speed" \
        or name == "attackspeed"


def IsMyStruct(name):
    '''
    reward 奖励模块
    enemy 敌人模块
    struct 通用结构
    '''
    return name[:len("reward")] == "reward" \
        or name[:len("struct")] == "struct"


def CheckMyStruct(fieldtype, fields):
    if fieldtype[:len("reward")] == "reward":
        nextfields = fieldtype[len("reward") + 1:-1].split(",")
        for index, parse in enumerate(nextfields + fields):
            if TList == parse[:len(TList)] or TStruct == parse[:len(TStruct)] or IsMyStruct(parse) or TNextLevel == parse[:len(TNextLevel)]:
                break
            assert parse.find("itemid") in [0, len("string:"), len("default:")]\
                or parse.find("count") in [0, len("int:"), len("float:"), len("default:")]\
                or parse.find("weight") in [0, len("int:"), len("float:"), len("default:")] or not parse,\
                "Error[非法的数据结构]: near " + fieldtype + \
                "\n" + str(nextfields + fields)
    else:
        assert not fieldtype, "Error[未识别的数据结构]: near " + fieldtype
    return nextfields


def CheckParses(fields):
    result = []
    while len(fields) > 0:
        # print fields
        field = fields.pop(0)
        if not field:
            parse = {'name': "", "func": None, "args": None}
            result.append(parse)
            continue
        if TNextLevel == field[:len(TNextLevel)]:  # 父子
            field = field[len(TNextLevel):]
            for index, val in enumerate(fields):
                if TNextLevel == val[:len(TNextLevel)]:
                    fields[index] = val[len(TNextLevel):]
        if TFileTag == field[:len(TFileTag)]:
            field = field[field.find(":") + 1:]
        parse = {"default": None, "args": None}
        typepos = field.rfind(":")
        fieldtype = field[:typepos]
        name = field[typepos + 1:]
        valuepos = name.rfind("=")
        if valuepos != -1:  # 设置默认值
            parse["default"] = name[valuepos + 1:]
            name = name[:valuepos]
        parse["name"] = ValToKey(name)
        # print fieldtype, name, parse
        if TDefault == fieldtype[:len(TDefault)]:  # 默认字段,只出现在list和struct中
            parse["func"] = TDefault
        elif TInt == fieldtype[:len(TInt)]:
            parse["func"] = TInt
        elif TBool == fieldtype[:len(TBool)]:
            parse["func"] = TBool
        elif TFloat == fieldtype[:len(TFloat)]:
            parse["func"] = TFloat
        elif TString == fieldtype[:len(TString)]:
            parse["func"] = TString
            if parse["default"] and parse["default"][:1] != "\"" and parse["default"][-1:] != "\"":
                parse["default"] = CheckString(parse["default"])
        elif typepos == -1 and IsMyInt0(name):
            fieldtype = TInt
            parse["func"] = TInt
            if not parse["default"]:
                parse["default"] = "0"
        elif typepos == -1 and IsMyInt(name):
            fieldtype = TInt
            parse["func"] = TInt
        elif typepos == -1 and IsMyFloat(name):
            fieldtype = TFloat
            parse["func"] = TFloat
            if not parse["default"]:
                parse["default"] = "0"
        elif typepos == -1 and IsMyString(name):
            fieldtype = TString
            parse["func"] = TString
            if parse["default"] and parse["default"][:1] != "\"" and parse["default"][-1:] != "\"":
                parse["default"] = CheckString(parse["default"])
        else:
            if TList == fieldtype[:len(TList)]:
                parse["func"] = TList
                nextfield = fieldtype[len(TList) + 1:-1]
                nextfields = IsMyStruct(nextfield) and [
                    nextfield + ":"] or ["struct<" + nextfield + ">:"]
                # print nextfields
            elif TStruct == fieldtype[:len(TStruct)]:
                parse["func"] = TStruct
                nextfields = fieldtype[len(TStruct) + 1:-1].split(",")
            elif IsMyStruct(fieldtype):
                parse["func"] = TStruct
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
            parse["args"] = CheckParses(nextfields + fields[:endpos])
            parse1 = parse["args"].pop()
            if parse1["func"] == TStruct:
                parse["args"].append(parse1)
                parse2 = parse1["args"].pop()
                if parse2["func"] == TList and parse["name"] == parse2["name"]:  # 父子合并
                    # if parse["args"] != parse2["args"]:
                    # 	debug("Warning "+)
                    parse["args"] += parse2["args"]
                else:
                    parse1["args"].append(parse2)
            elif parse1["func"] == TList and parse["name"] == parse1["name"]:
             # and parse["args"] == parse1["args"]: #父子合并
                parse["args"] += parse1["args"]
            else:
                parse["args"].append(parse1)
            # print parse
            fields = fields[endpos:]
        # if len(result) > 0:
        # 	print parse," += ",result[len(result)-1]
        if len(result) > 0 and parse["func"] == TList and parse["name"] == result[len(result) - 1]["name"]:
            # and (parse["args"] == result[len(result)-1]["args"] or (type(result[len(result)-1]["args"]) is list \
            # and parse["args"] == result[len(result)-1]["args"][:1])): #同级合并
            parse["args"] += result[len(result) - 1]["args"]
            result.pop()
        for index, parse1 in enumerate(result):
            assert parse["name"] != parse1["name"], "Error[重复的字段]: near " + \
                field + "\n" + str(result)
        result.append(parse)
    # print result
    return result


def ValToKey(val):
    return val.isdecimal() and "[" + val + "]" or val


def CheckInt(data, args=None):
    if len(data) == 0:
        assert args != "key", "Error[主键不能为空]: near " + sheetname + \
            filename + "(" + GetColNum(mycol) + str(myrow + 1) + ")"
        assert args != None, "Error[字段不能为空]: near " + sheetname + \
            filename + "(" + GetColNum(mycol) + str(myrow + 1) + ")"
        return args
    vals = data.split('.')
    assert len(vals) == 2 and vals[1] == "0", "Error[非法的整型]: found " + data + \
        " near " + sheetname + filename + \
        "(" + GetColNum(mycol) + str(myrow + 1) + ")"
    return vals[0]


def CheckBool(data, args=None):
    if len(data) == 0:
        assert args, "Error[字段不能为空]: near " + sheetname + \
            filename + "(" + GetColNum(mycol) + str(myrow + 1) + ")"
        return args
    return "0.0" == data and "false" or "true"


def CheckFloat(data, args=None):
    if len(data) == 0:
        assert args, "Error[字段不能为空]: near " + sheetname + \
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
    for index, parse in enumerate(parses):
        if parse["name"] == name:
            return col1, True
        elif parse["func"] == TDefault:
            continue
        elif parse["func"] == TStruct:
            col, result = getColByName(parse["args"], name)
            col1 += col
        elif parse["func"] == TList:
            col, result = getColByName(parse["args"], name)
            col1 += col
        else:  # 跳过空字段或基础字段
            col1 += 1
        if result:
            return col1, True
    return col1, result


def GetColNum(col):
    if col >= 26:
        return "A" + chr(col + 65 - 26)
    return chr(col + 65)


def GetCols(parse):
    return str(parse).count('func') - str(parse).count('func\': \'' + TDefault) - str(parse).count('func\': \'' + TList) - str(parse).count('func\': \'' + TStruct)

def CheckChunk(parses, sheet, row1, row2, col, indent, nodename):
    global sheetname
    global filename
    global myrow
    global mycol
    global imglacks
    sheetname = sheet.name
    filename = GetValue(sheet, 0, 0)
    luachunks = []
    jschunks = []
    jsonchunks = []
    xmlchunks = []
    while row1 < row2:
        myrow = row1
        col1 = col
        luachunk = []
        jschunk = []
        jsonchunk = []
        xmlchunk = []
        majorkey = None
        newrow2 = GetNextRow(sheet, row1 + 1, row2, col)
        # print "parse row", row1, newrow2
        for index, parse in enumerate(parses):
            mycol = col1
            field = parse["func"] == TDefault and parse["default"] or GetValue(
                sheet, row1, col1)
            key = parse["name"]
            # print myrow, mycol, parse["func"], key, field
            if parse["func"] == TDefault:
                assert parse["default"], "Error[无效的默认值]: near " + sheetname + \
                    filename + "(" + GetColNum(mycol) + str(myrow + 1) + ")"
                luachunk.append(key + " = " + parse["default"])
                jschunk.append(key + ":" + parse["default"])
                jsonchunk.append("\"" + key + "\":" + parse["default"])
                xmlchunk.append(key + " = " + Quotes(parse["default"]))
                continue
            elif parse["func"] == TInt:
                val = CheckInt(field, parse["default"])
                luachunk.append(key and key + " = " + val or val)
                jschunk.append(key and key + ":" + val or val)
                jsonchunk.append(key and "\"" + key + "\":" + val or val)
                xmlchunk.append(key and key + " = " +
                                Quotes(val) or Quotes(val))
                if parse["default"] == "key":
                    assert not majorkey, "Error[重复的主键]: near " + sheetname + \
                        filename + "(" + GetColNum(mycol) + \
                        str(myrow + 1) + ")"
                    majorkey = "" + str(val) + ""
                col1 += 1
            elif parse["func"] == TBool:
                value = CheckBool(field, parse["default"])
                luachunk.append(key + " = " + value if key else value)
                jschunk.append(key + " : " + value if key else value)
                jsonchunk.append("\"" + key + "\":" + value if key else value)
                xmlchunk.append(key + " = " + Quotes(value)
                                if key else Quotes(value))
                col1 += 1
            elif parse["func"] == TFloat:
                value = CheckFloat(field, parse["default"])
                luachunk.append(key and key + " = " + value or value)
                jschunk.append(key and key + ":" + value or value)
                jsonchunk.append(key and "\"" + key + "\":" + value or value)
                xmlchunk.append(key and key + " = " +
                                Quotes(value) or Quotes(value))
                col1 += 1
            elif parse["func"] == TString:
                val = CheckString(field, parse["default"])
                if val != "\"\"" and key in ["img", "icon"]:
                    rval = val[1:-1]
                if val != "\"\"" or not key in ["img", "ccbi", "starttime", "endtime"]:
                    luachunk.append(key and key + " = " + val or val)
                    jschunk.append(key and key + ":" + val or val)
                    jsonchunk.append(key and "\"" + key +
                                     "\":" + Quotes(val) or Quotes(val))
                if not key in ["img", "desc", "answer"]:
                    xmlchunk.append(key and key + " = " + Quotes(CheckString(
                        field, parse["default"])) or Quotes(CheckString(field, parse["default"])))
                if parse["default"] == '"key"':
                    assert not majorkey, "Error[重复的主键]: near " + sheetname + \
                        filename + "(" + GetColNum(mycol) + \
                        str(myrow + 1) + ")"
                    majorkey = "" + str(val) + ""
                col1 += 1
            elif parse["func"] == TStruct:
                if not GetValue(sheet, row1, col1) and parse["args"][0]["default"] == None:
                    col1 += GetCols(parse["args"])
                else:
                    col1, lua, js, json, xml = CheckChunk(
                        parse["args"], sheet, row1, newrow2, col1, indent, key and key or nodename)
                    if lua[len(indent) + 1:len(indent) + 2] == "[":
                        luachunk.append(lua)
                        jschunk.append(js)
                        jsonchunk.append(json)
                    elif lua:
                        luachunk.append(
                            key and key + " = {" + lua + "}" or "{" + lua + "}")
                        jschunk.append(
                            key and key + ":{" + js + "}" or "{" + js + "}")
                        jsonchunk.append(key and "\"" + key +
                                         "\":{" + json + "}" or "{" + json + "}")
                    if xml != "" and (not (key and key or nodename) in ["increase", "states", "skill"]):
                        xmlchunk.append((len(xmlchunk) > 0 and xmlchunk[len(
                            xmlchunk) - 1][-1:] != ">") and ">" + xml or xml)
            elif parse["func"] == TList:
                col1, lua, js, json, xml = CheckChunk(
                    parse["args"], sheet, row1, newrow2, col1, indent + "  ", key)
                if xml != "":
                    xmlchunk.append((len(xmlchunk) > 0 and xmlchunk[len(
                        xmlchunk) - 1][-1:] != ">") and ">" + xml or xml)
                if parse["default"] == "key":
                    key = ValToKey(CheckInt(field))
                luachunk.append("\n" + indent + "  " +
                                key + " = {" + lua + "}")
                jschunk.append("\n" + indent + "  " + key + ":[" + js + "]")
                jsonchunk.append("\n" + indent + "  " +
                                 "\"" + key + "\":[" + json + "]")
            else:  # 跳过空字段
                assert parse["func"] == None, "Error[非法的字段名]: near " + sheetname + \
                    filename + "(" + GetColNum(mycol) + str(myrow + 1) + ")"
                col1 += 1
            # print luachunk[len(luachunk)-1]
        xml = " ".join(xmlchunk)
        assert xml[-1:] == '"' or xml[-1:] == '>' or xml[-1:] == '', "A" + xml + "A"
        if xml != "":
            xmlchunks.append((xml[:1] == ">" or xml[:1] == "\n") and xml or "\n" + indent + "<" +
                             nodename + " " + xml + (xml[-1:] == '"' and ">" or "") + "</" + nodename + ">")
        if majorkey:
            luachunks.append(
                "\n" + indent + "[" + majorkey + "]" + " = {" + ", ".join(luachunk) + "}")
            jschunks.append("\n" + indent + majorkey +
                            ":{" + ", ".join(jschunk) + "}")
            jsonchunks.append("\n" + indent + Quotes(majorkey) +
                              ":{" + ", ".join(jsonchunk) + "}")
        elif len(luachunk) > 0:  # 列表比如{1,2,3}
            luachunks.append(", ".join(luachunk))
            jschunks.append(", ".join(jschunk))
            jsonchunks.append(", ".join(jsonchunk))
        row1 = newrow2
    return col1, ", ".join(luachunks), ", ".join(jschunks), ", ".join(jsonchunks), " ".join(xmlchunks)


def Quotes(val):
    if val[:1] == '"':
        return val
    return '"' + val + '"'


def GetNextRow(sheet, row1, row2, col):
    for newrow1 in range(row1, row2):
        if len(GetValue(sheet, newrow1, col)) != 0:
            return newrow1
    return row2

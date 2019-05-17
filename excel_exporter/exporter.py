#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import codecs
import os

import xlrd

from .check_chunk import ParseSheet, ProcessSheet
from .config import config
from .log import debug, info, set_debug_mode

sheetfields = {}
output_path = './output/'


def get_value(sheet, row, col):
    return str(sheet.cell(row, col).value).strip()


def get_line(sheet, row):
    return [get_value(sheet, row, col) for col in range(0, sheet.ncols)]


def save_to_file(target, filename, file_type, txt):
    file_full_name = os.path.join(
        output_path, target, file_type, "{0}.{1}".format(filename, file_type))
    with codecs.open(file_full_name, "w", "utf-8") as f:
        f.write(txt)


def export_workbook(workbook_path, check_config):
    info("Reading " + workbook_path)
    workbook = xlrd.open_workbook(workbook_path)
    for sheet in workbook.sheets():
        if sheet.nrows < 3:
            continue
        #	第一行注释
        #	第二行导出选项
        #   第三行类型
        cursor = 0
        filename = get_value(sheet, cursor, 0)
        sheetname = sheet.name
        if filename is '':
            continue
        # 调试的时候方便只导出某一sheet
        # if filename != 'package':
        #     continue
        info("Exporting {} {} ......".format(sheetname, filename))
        sheetfields[filename] = ""
        cursor = 2
        line = get_line(sheet, cursor)
        for field in line:
            sheetfields[filename] += field + "\\\n"
        parses = ParseSheet(line, check_config)
        debug(parses)
        cursor = 1
        for target, flag in config['target'].items():
            target_parses = parses.copy()
            continue_flag = False
            for col in range(0, len(target_parses)):
                option = sheet.cell(cursor, col).value
                try:
                    option = int(option)
                except:
                    option = 0
                if option & flag == 0:
                    if col == 0:
                        continue_flag = True
                        break
                    else:
                        target_parses[col] = None
            if continue_flag:
                continue
            ast = ProcessSheet(target_parses, sheet, 3)
            result = {}
            # 在此进行文件内容的校验并导出
            for file_type, conf in config['outputFileTypes'].items():
                if not conf['enable']:
                    continue
                result[file_type] = conf['convert_func'](ast)
                if 'file_structs' in conf:
                    result[file_type] = conf['file_structs'].format(
                        filename, result[file_type])
                # 格式化
                if conf['format'] and conf['format_func']:
                    format_func = conf['format_func'].__call__
                    result[file_type] = format_func(result[file_type])
                # 保存到文件
                save_to_file(target, filename, file_type, result[file_type])


def export(wb_paths, check_config):
    # 生成对应目录
    for file_type, conf in config['outputFileTypes'].items():
        if(conf['enable']):
            for target, flag in config['target'].items():
                os.makedirs(os.path.join(
                    output_path, target, file_type), exist_ok=True)

    for wb_path in wb_paths:
        basename = os.path.basename(wb_path)
        extname = os.path.splitext(basename)[-1]
        if not basename.startswith('~$'):
            if extname == '.xls' or extname == '.xlsx':
                export_workbook(wb_path, check_config)

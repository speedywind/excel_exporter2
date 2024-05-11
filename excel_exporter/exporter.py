#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import codecs
import os

import xlrd

from .check_chunk import ParseSheet, ProcessSheet, GetColNum, FormatSheet, is_localize
from .config import config
from .log import debug, info, set_debug_mode

output_path = './output/'


class Sheet():
    def __init__(self, sheet):
        self.title = sheet.name
        self.values = []
        output_types = sheet.row_values(2)
        while(output_types[-1] == ""):
            output_types.pop()
        ncols = len(output_types)
        for row_i in range(sheet.nrows):
            row_list = []
            self.values.append(row_list)
            for col_i in range(ncols):
                cell = sheet.cell(row_i, col_i)
                ctype = cell.ctype
                cell = cell.value
                if ctype == xlrd.XL_CELL_EMPTY:
                    cell = None
                elif ctype == xlrd.XL_CELL_NUMBER:
                    cell_int = int(cell)
                    if cell_int == cell:
                        cell = cell_int
                    cell = str(cell)
                else:
                    assert ctype == xlrd.XL_CELL_TEXT, "Error[非法的数据结构]: found {} near {} ({}{})".format(
                        cell, self.title, GetColNum(col_i+1), str(row_i+1))
                    if cell == "":
                        cell = None
                row_list.append(cell)
        self.max_row = len(self.values)+1

    def __getitem__(self, row):
        return self.values[row-1]

    def __setitem__(self, row, value):
        self.values[row-1] = value

    def cell(self, row, col):
        assert(row > 0 and col > 0)
        return self.values[row-1][col-1]


def get_value(sheet, row, col):
    return sheet.cell(row, col)


def get_str_value(sheet, row, col):
    return str(get_value(sheet, row, col) or "")


def get_line(sheet, row):
    return [cell for cell in sheet[row]]


def get_str_line(sheet, row):
    return [str(cell or "") for cell in sheet[row]]


def save_to_file(target, filename, file_type, txt):
    os.makedirs(os.path.join(output_path, target, file_type), exist_ok=True)
    file_full_name = os.path.join(
        output_path, target, file_type, "{0}.{1}".format(filename, file_type))
    with codecs.open(file_full_name, "w", "utf-8") as f:
        f.write(txt)


def export_workbook(workbook_path, check_config, localizes):
    info("Reading " + workbook_path)
    workbook = xlrd.open_workbook(workbook_path)
    for localize in localizes:
        for target, types in config['target'].items():
            ast = ""
            keys_num = 0
            for sheetx in range(workbook.nsheets):
                worksheet = workbook._sheet_list[sheetx]
                if not worksheet:
                    break
                if worksheet.nrows <= 3:
                    continue
                #	第一行注释    comment
                #	第二行导出选项 output_option
                #   第三行导出类型 output_type
                sheetname = worksheet.name
                filename = worksheet.cell_value(0, 0)
                if filename == '':
                    continue
                sheet = Sheet(worksheet)
                # 调试的时候方便只导出某一sheet
                # if filename != 'activity_date':
                #     continue
                info("Exporting {} {} for {} ......".format(sheetname, filename, target+"_"+localize))

                # 生成多导出目标 sheet
                row_output_type = list(sheet[3])
                sheet_for_target = sheet
                sheet_for_target[3] = list(row_output_type)
                for i, annotate in enumerate(sheet_for_target[1]):
                    if is_localize(annotate) and annotate.find(localize) < 0:
                        sheet_for_target[3][i] = None
                for i, output_option in enumerate(sheet_for_target[2]):
                    if (int(output_option or 0)) & types['flag'] == 0:
                        sheet_for_target[3][i] = None
                row = 3
                output_type = get_str_line(sheet_for_target, row)
                parses = ParseSheet(output_type, check_config)
                row = 4
                parses[0].localize = localize
                py, num = ProcessSheet(parses, sheet_for_target, row)
                ast += py
                keys_num += num
                if len(ast) == 0:
                    continue
                # 根据下一张表的内容判断是否进行导出,下一张表有相同内容时导出到一张表
                worksheet = sheetx+1 < workbook.nsheets and workbook._sheet_list[sheetx+1] or None
                if worksheet and worksheet.nrows > 3 and filename == worksheet.cell_value(0, 0):
                    FormatSheet(ast)
                    ast += ","
                    continue
                ast = FormatSheet(ast)
                assert len(ast) == keys_num, "Error[重复的主键]: near " + sheetname
                export_sheet(target+"_"+localize, filename, types, ast)
                ast = ""
                keys_num = 0

def export_sheet(path, filename, types, ast):
    result = {}
    # 在此进行文件内容的校验并导出
    for file_type in types['output']:
        conf = config['outputFileTypes'][file_type]
        result = conf['convert_func'](ast)
        if 'file_structs' in conf:
            result = conf['file_structs'].format(
                filename, result)
        # 格式化
        if conf['format'] and conf['format_func']:
            format_func = conf['format_func'].__call__
            result = format_func(result)
        # 保存到文件
        save_to_file(path, filename, file_type, result)

def export(wb_paths, check_config, localizes):
    # 生成对应目录
    for localize in localizes:
        for target, types in config['target'].items():
            for file_type in types['output']:
                os.makedirs(os.path.join(output_path, target+"_"+localize, file_type), exist_ok=True)

    for wb_path in wb_paths:
        basename = os.path.basename(wb_path)
        extname = os.path.splitext(basename)[-1]
        if not basename.startswith('~$'):
            if extname == '.xls' or extname == '.xlsx':
                export_workbook(wb_path, check_config, localizes)

    for localize in localizes:
        for target, types in config['target'].items():
            for file_type in types['output']:
                path = os.path.join(output_path, target+"_"+localize, file_type)
                files = []
                for filename in os.listdir(path):
                    name, extension = os.path.splitext(filename)
                    if extension == "."+file_type and name != "files":
                        files.append(name)
                export_sheet(target+"_"+localize, "files", types, files)


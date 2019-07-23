#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import codecs
import os

import openpyxl

from .check_chunk import ParseSheet, ProcessSheet
from .config import config
from .log import debug, info, set_debug_mode

output_path = './output/'


def get_value(sheet, row, col):
    return sheet.cell(row, col).value


def get_str_value(sheet, row, col):
    return str(get_value(sheet, row, col) or "").strip()


def get_line(sheet, row):
    return [cell.value for cell in sheet[row]]


def get_str_line(sheet, row):
    return [str(cell.value or "").strip() for cell in sheet[row]]


def save_to_file(target, filename, file_type, txt):
    file_full_name = os.path.join(
        output_path, target, file_type, "{0}.{1}".format(filename, file_type))
    with codecs.open(file_full_name, "w", "utf-8") as f:
        f.write(txt)


def export_workbook(workbook_path, check_config):
    info("Reading " + workbook_path)
    workbook = openpyxl.load_workbook(workbook_path, data_only=True)
    workbook.guess_types = True
    for sheet in workbook:
        if sheet.max_row < 3:
            continue
        #	第一行注释    comment
        #	第二行导出选项 output_option
        #   第三行导出类型 output_type
        row = 1
        filename = get_str_value(sheet, row, 1)
        sheetname = sheet.title
        if filename is '':
            continue
        # 调试的时候方便只导出某一sheet
        # if filename != 'package':
        #     continue
        info("Exporting {} {} ......".format(sheetname, filename))

        # 生成多导出目标 sheet
        for target, flag in config['target'].items():
            sheet_for_target = workbook.copy_worksheet(sheet)
            sheet_for_target.title = sheetname+"#"+target
            for col in sheet_for_target.columns:
                if (col[1].value or 0) & flag == 0:
                    col[2].value = None
            row = 3
            output_type = get_str_line(sheet_for_target, row)
            parses = ParseSheet(output_type, check_config)
            row = 4
            ast = ProcessSheet(parses, sheet_for_target, row)
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

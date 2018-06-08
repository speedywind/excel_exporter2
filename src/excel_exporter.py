#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import argparse
import codecs
import os
import json

import xlrd

from config import config
from check_chunk import ProcessSheet, ParseSheet
from log import debug, set_debug_mode

sheetfields = {}
output_path = './output/'


def get_value(sheet, row, col):
    return str(sheet.cell(row, col).value).strip()


def get_line(sheet, row):
    return [get_value(sheet, row, col) for col in range(0, sheet.ncols)]


def save_to_file(filename, file_type, txt):
    file_full_name = os.path.join(
        output_path, file_type, "{0}.{1}".format(filename, file_type))
    with codecs.open(file_full_name, "w", "utf-8") as f:
        f.write(txt)


def export_workbook(workbook_path, check_config):
    print("Reading " + workbook_path)
    workbook = xlrd.open_workbook(workbook_path)
    for sheet in workbook.sheets():
        if sheet.nrows < 3:
            continue
        #	第一行注释
        #	第二行类型
        debug(get_line(sheet, 1))
        filename = get_value(sheet, 0, 0)
        sheetname = sheet.name
        if filename is '':
            continue
        print("Exporting {} {} ......".format(sheetname, filename))
        sheetfields[filename] = ""
        for field in get_line(sheet, 1):
            sheetfields[filename] += field + "\\\n"
        parses = ParseSheet(get_line(sheet, 1), check_config)
        debug(parses)
        # 第三行内容
        result = ProcessSheet(parses, sheet, 2)
        ast = json.loads(result['json'])
        # 在此进行文件内容的校验
        for file_type, conf in config.items():
            if not conf['enable']:
                continue
            if conf['native']:
                if filename in conf['except_files']:
                    continue
            else:
                # 非原生语言，从dict转换
                result[file_type] = conf['convert_func'](ast)
            if 'file_structs' in conf:
                result[file_type] = conf['file_structs'].format(
                    filename, result[file_type])
            # 格式化
            if conf['format'] and conf['format_func']:
                format_func = conf['format_func'].__call__
                result[file_type] = format_func(result[file_type])
            # 保存到文件
            save_to_file(filename, file_type, result[file_type])


def export(wb_paths, check_config):
    # 生成对应目录
    for file_type, conf in config.items():
        if(conf['enable']):
            os.makedirs(os.path.join(output_path, file_type), exist_ok=True)

    for wb_path in wb_paths:
        if wb_path.endswith('.xls') or wb_path.endswith('.xlsx'):
            export_workbook(wb_path, check_config)


def main():
    parser = argparse.ArgumentParser(
        prog='excel_exporter',
        description='export excel configuration to lua/js/json/xml')
    parser.add_argument('--version', action='version',
                        version='%(prog)s 0.1.0-alpha')
    parser.add_argument('workbooks', help='name of workbooks', nargs='*')
    parser.add_argument('-c', '--check_config',
                        help='config for check contents of sheets')
    parser.add_argument('-d', '--directory', help='directory of workbooks')
    parser.add_argument('-o', '--output', help='output directory')
    parser.add_argument('-v', '--verbosity', action="count",
                        help="increase output verbosity")
    args = parser.parse_args()
    if args.verbosity:
        set_debug_mode(True)

    if args.output:
        global output_path
        output_path = args.output

    if args.check_config:
        with open(args.check_config, 'r') as config_file:
            check_config = json.load(config_file)
            for k in check_config:
                l = check_config[k]
                for i in range(len(l)):
                    l[i] = l[i].replace('*', r'\w*')
                    l[i] = l[i].replace('?', r'\w')
                    l[i] = r"\b{}\b".format(l[i])  # 全文匹配

    if args.workbooks:
        export(args.workbooks, check_config)

    if args.directory:
        export([os.path.join(args.directory, filename)
                for filename in os.listdir(args.directory)], check_config)


if __name__ == "__main__":
    main()

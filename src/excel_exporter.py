#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import argparse
import codecs
import os

import xlrd

from check_chunk import CheckChunk, CheckParses
from log import debug, set_debug_mode

sheetfields = {}
output_path = './output/'
file_types = ['lua', 'js', 'json', 'xml']
except_files = {
    'lua': [],
    'js': [],
    'json': [],
    'xml': [],
}


def get_value(sheet, row, col):
    return str(sheet.cell(row, col).value).strip()


def get_line(sheet, row):
    return [get_value(sheet, row, col) for col in range(0, sheet.ncols)]


def export_workbook(workbook_path):
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
        parses = CheckParses(get_line(sheet, 1))
        debug(parses)
        # 第三行内容
        col, lua, js, json, xml = CheckChunk(
            parses, sheet, 2, sheet.nrows, 0, "", "data")
        # 在此进行文件内容的校验
        file_structs = {
            'lua': "-- {0}\nreturn {{{1}}}",
            'js': "// {0}\nmodule.exports = {{{1}}}",
            'json': "{{{1}}}",
            'xml': "<data>{1}</data>",
        }
        for file_type in file_types:
            if not filename in except_files[file_type]:
                with codecs.open(os.path.join(output_path, file_type, "{0}.{1}".format(filename, file_type)), "w", "utf-8") as f:
                    f.write(file_structs[file_type].format(
                        filename, locals()[file_type]))


def export(wb_paths):
    # 生成对应目录
    for file_type in file_types:
        os.makedirs(os.path.join(output_path, file_type), exist_ok=True)

    for wb_path in wb_paths:
        if wb_path.endswith('.xls') or wb_path.endswith('.xlsx'):
            export_workbook(wb_path)


def main():
    parser = argparse.ArgumentParser(
        prog='excel_exporter',
        description='export excel configuration to lua/js/json/xml')
    parser.add_argument('--version', action='version',
                        version='%(prog)s 0.1.0-alpha')
    parser.add_argument('workbooks', help='name of workbooks', nargs='*')
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

    if args.workbooks:
        export(args.workbooks)

    if args.directory:
        export([os.path.join(args.directory, filename)
                for filename in os.listdir(args.directory)])


if __name__ == "__main__":
    main()

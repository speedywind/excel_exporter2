#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

__version__ = "0.2.0"

import argparse
import json
import codecs
import os
from excel_exporter.config import config
from excel_exporter import exporter
from excel_exporter.log import debug, set_debug_mode

def run(args):
    if args.verbosity:
        set_debug_mode(True)

    if args.output:
        exporter.output_path = args.output

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
        exporter.export(args.workbooks, check_config)

    localizes = {"zh_cn", "zh_tw"}
    if args.localize:
        localizes = {args.localize}
    if args.json:
        wb_paths = [os.path.join(args.directory, filename)
            for filename in os.listdir(args.directory)]
        for wb_path in wb_paths:
            basename = os.path.basename(wb_path)
            extname = os.path.splitext(basename)[-1]
            if extname == '.json':
                print(basename)
                basename = basename.replace(extname, "")
                with codecs.open(wb_path, "r", "utf-8") as f:
                    ast = json.loads(f.read())
                    for localize in localizes:
                        for target, types in config['target'].items():
                            exporter.export_sheet(target+"_"+localize, basename, types, ast)
    elif args.directory:
        exporter.export([os.path.join(args.directory, filename)
                         for filename in os.listdir(args.directory)], check_config, localizes)

def main():
    parser = argparse.ArgumentParser(
        prog='excel_exporter',
        description='export excel configuration to lua/js/json/xml')
    parser.add_argument('--version', action='version',
                        version='%(prog)s '+__version__)
    parser.add_argument('workbooks', help='name of workbooks', nargs='*')
    parser.add_argument('-c', '--check_config',
                        help='config for check contents of sheets')
    parser.add_argument('-d', '--directory', help='directory of workbooks')
    parser.add_argument('-json', '--json', action="count", help='input json')
    parser.add_argument('-o', '--output', help='output directory')
    parser.add_argument('-v', '--verbosity', action="count",
                        help="increase output verbosity")
    parser.add_argument('-l', '--localize', help="zh_cn/zh_tw")
    args = parser.parse_args()

    run(args)


if __name__ == "__main__":
    profile = False
    if profile:
        import cProfile
        cProfile.run("main()")
    else:
        main()
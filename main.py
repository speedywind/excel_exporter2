#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

__version__ = "0.2.0"

import argparse
import json
import os

from excel_exporter import exporter
from excel_exporter.log import debug, set_debug_mode


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
    parser.add_argument('-o', '--output', help='output directory')
    parser.add_argument('-v', '--verbosity', action="count",
                        help="increase output verbosity")
    args = parser.parse_args()
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

    if args.directory:
        exporter.export([os.path.join(args.directory, filename)
                         for filename in os.listdir(args.directory)], check_config)


if __name__ == "__main__":
    main()

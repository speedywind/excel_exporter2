#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

from main import __version__

from setuptools import setup, find_packages

with open('README.md', encoding="utf-8") as f:
    readme = f.read()

with open('LICENSE', encoding="utf-8") as f:
    license = f.read()

setup(
    name='excel_exporter',
    version=__version__,
    description='Sample tool to export lua/json/xml from excel files',
    long_description=readme,
    author='Sean Feng',
    author_email='sean@fantablade.com',
    url='https://git.fantablade.cn/FantaBlade/WaterGun/excel_exporter',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

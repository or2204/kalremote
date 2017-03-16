#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

dynamic_requires = []

version = 0.1

setup(
    name='kalremote',
    version=0.1,
    author='Olga Shafer',
    author_email='####',
    url='http://github.com/or2204/kalremote',
    packages=find_packages(),
    scripts=[],
    install_requires=['pycrypto==2.6.1'],
    description='####',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
    ],
    include_package_data=True,
    zip_safe=False,
)

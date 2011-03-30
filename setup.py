#!/usr/bin/python
# -*- coding: utf-8 -*-

# libthumbor - python extension to thumbor
# https://github.com/heynemann/libthumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

import os
from setuptools import setup
from libthumbor import __version__

setup(
    name = 'libthumbor',
    version = __version__,
    description = "libthumbor is the python extension to thumbor",
    long_description = """
libthumbor is the python extension to thumbor.
It allows users to generate safe urls easily.
""",    
    keywords = 'imaging face detection feature thumbor thumbnail imagemagick pil opencv',
    author = 'Bernardo Heynemann',
    author_email = 'heynemann@gmail.com',
    url = 'https://github.com/heynemann/libthumbor/wiki',
    license = 'MIT',
    classifiers = ['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: English',
                   'Operating System :: MacOS',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 2.6',
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                   'Topic :: Multimedia :: Graphics :: Presentation'
    ],
    packages = ['libthumbor'],
    package_dir = {"libthumbor": "libthumbor"},
    include_package_data = True,
    package_data = {
    },

    install_requires=[
        "pyDes"
    ],
)



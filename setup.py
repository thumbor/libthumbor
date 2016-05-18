#!/usr/bin/python
# -*- coding: utf-8 -*-

# libthumbor - python extension to thumbor
# http://github.com/heynemann/libthumbor

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

'''Module that configures setuptools to package libthumbor'''

from setuptools import setup, find_packages

tests_require = [
    'mock',
    'nose',
    'coverage',
    'yanc',
    'preggy',
    'flake8',
]

setup(
    name='libthumbor',
    version="1.3.2",
    description="libthumbor is the python extension to thumbor",
    long_description="""
libthumbor is the python extension to thumbor.
It allows users to generate safe urls easily.
""",
    keywords='imaging face detection feature thumbor thumbnail' +
             ' imagemagick pil opencv',
    author='Bernardo Heynemann',
    author_email='heynemann@gmail.com',
    url='http://github.com/heynemann/libthumbor',
    license='MIT',
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Natural Language :: English',
                 'Operating System :: MacOS',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 2.6',
                 'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                 'Topic :: Multimedia :: Graphics :: Presentation'
                 ],
    packages=find_packages(),
    package_dir={"libthumbor": "libthumbor"},
    include_package_data=True,
    package_data={
    },

    extras_require={
        'tests': tests_require,
    },

    install_requires=[
        "six"
    ],
)

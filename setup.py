#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import codecs
from setuptools import setup, find_packages
#from distribute import setup, find_packages
import djintegration

import os
templates_dirs = []
for directory in os.walk('djintegration/templates'):
    templates_dirs.append(directory[0][6:]+'/*.*')

setup(
    name='djintegration',
    version=djintegration.__version__,
    description=djintegration.__doc__,
    author=djintegration.__author__,
    author_email=djintegration.__contact__,
    url=djintegration.__homepage__,
    platforms=["any"],
    packages=find_packages(exclude=['testproj', 'testproj.*']),
    package_data={'djintegration': templates_dirs},
    zip_safe=False,
    test_suite="nose.collector",
    install_requires=(
        'nose',
        'django',
        'virtualenv',
        #'coverage',
    ),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    long_description=codecs.open('README', "r", "utf-8").read(),
)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
import os
from setuptools import setup, find_packages
# http://peak.telecommunity.com/DevCenter/setuptools#developer-s-guide


def content_of(*files):
    import codecs
    open = lambda path: codecs.open(path, encoding='utf-8')
    here = os.path.abspath(os.path.dirname(__file__))
    content = []
    for f in files:
        with open(os.path.join(here, f)) as stream:
            content.append(stream.read())
    return '\n'.join(content)

setup(
    name="release",
    description='Automates the process of releasing a new version of '
    'some software.',
    long_description=content_of('README.rst', 'CHANGES.rst'),
    url='https://github.com/nandoflorestan/release',
    version='0.1.0dev',
    license='MIT',
    author='Nando Florestan',
    author_email="nandoflorestan@gmail.com",
    install_requires=['nine', 'bag', 'grimace', 'requests'],
    classifiers=[  # http://pypi.python.org/pypi?:action=list_classifiers
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords=['python', 'software', 'release', 'releaser', 'automation',
              'git', 'hg', 'setup.py', 'setuptools', 'distribute',
    ],
    packages=find_packages(),
    include_package_data=True,
    # test_suite='release.tests',
    zip_safe=False,
)

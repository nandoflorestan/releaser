#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
import os
from setuptools import setup, find_packages
# http://peak.telecommunity.com/DevCenter/setuptools#developer-s-guide


def content_of(*files):
    """Given 1 or more file paths, returns their content in a single string."""
    import codecs
    here = os.path.abspath(os.path.dirname(__file__))
    content = []
    for f in files:
        with codecs.open(os.path.join(here, f), encoding='utf-8') as stream:
            content.append(stream.read())
    return '\n'.join(content)

dependencies = [
    'nine > 0.3.2', 'bag > 0.3.7', 'docutils', 'grimace == 0.0.14', 'path.py',
    'requests', 'wheel']

setup(
    name="releaser",
    description='Automates the process of releasing a new version of '
    'some software.',
    long_description=content_of('README.rst', 'CHANGES.rst'),
    url='https://github.com/nandoflorestan/releaser',
    version='1.1.0',
    license='MIT',
    author='Nando Florestan',
    author_email="nandoflorestan@gmail.com",
    install_requires=dependencies,
    classifiers=[  # http://pypi.python.org/pypi?:action=list_classifiers
        'Development Status :: 5 - Production/Stable',
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
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords=['python', 'software', 'release', 'releaser', 'automation',
              'git', 'hg', 'setup.py', 'setuptools', 'distribute',
              ],
    packages=find_packages(),
    include_package_data=True,
    # test_suite='releaser.tests',
    zip_safe=False,
)

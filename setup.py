#!/usr/bin/env python3

"""Installer for the *releaser* utility."""

import os
from setuptools import setup, find_packages

# http://peak.telecommunity.com/DevCenter/setuptools#developer-s-guide


def content_of(*files):
    """Given 1 or more file paths, return their content in a single string."""
    here = os.path.abspath(os.path.dirname(__file__))
    content = []
    for f in files:
        with open(os.path.join(here, f), encoding="utf-8") as stream:
            content.append(stream.read())
    return "\n".join(content)


dependencies = [
    "bag > 0.3.7",
    "docutils < 0.18",
    "grimace == 0.0.14",  # TODO version 0.1.2
    "requests",
    "wheel",
]

setup(
    name="releaser",
    description="Automates the process of releasing a new version of " "some software.",
    long_description=content_of("README.rst", "CHANGES.rst"),
    url="https://github.com/nandoflorestan/releaser",
    version="2.0.1",
    license="MIT",
    author="Nando Florestan",
    author_email="nandoflorestan@gmail.com",
    install_requires=dependencies,
    classifiers=[  # http://pypi.python.org/pypi?:action=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=[
        "python",
        "software",
        "release",
        "releaser",
        "automation",
        "git",
        "hg",
        "setup.py",
        "setuptools",
        "distribute",
        "pip",
    ],
    packages=find_packages(),
    include_package_data=True,
    # test_suite='releaser.tests',
    zip_safe=False,
)

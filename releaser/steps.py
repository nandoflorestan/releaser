#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import requests
from bag.console import bool_input
from nine import input
from . import ReleaseStep, StopRelease, system, system_or_stop
from .regex import version_in_python_source_file


class Shell(ReleaseStep):
    '''Runs some shell command.'''
    ERROR_CODE = 2

    def __init__(self, command, stop_on_failure=True):
        super(Shell, self).__init__()
        self.command = command
        self.stop_on_failure = stop_on_failure

    def __call__(self):
        if self.stop_on_failure:
            system_or_stop(self.command)
        else:
            system(self.command)


class InteractivelyApproveDistribution(ReleaseStep):
    '''Generate a source distribution and let the user verify that
    all files are in there.
    '''
    ERROR_CODE = 3

    def __call__(self):
        system_or_stop('python setup.py sdist')
        # TODO: Optionally xdg-open the archive for convenience
        # Create the sdist with "-d <output_dir>"  on a temp dir.
        # Delete it at the end.
        print("A source distribution has been generated. This is your chance ")
        print("to open the archive (in the 'dist' directory) ")
        print("and check that all files are in there.")
        if not bool_input("Do you approve the archive contents?"):
            raise StopRelease('If the distribution is missing some files,\n'
                "try correcting your MANIFEST.in file according to\n"
                "http://docs.python.org/3/distutils/sourcedist.html"
                "#specifying-the-files-to-distribute")


class CheckTravis(ReleaseStep):
    '''Checks the status, on travis-ci.org, of the latest build of a
    software project in a certain branch.
    '''
    ERROR_CODE = 91
    URL = 'https://api.travis-ci.org/repos/' \
          '{github_user}/{github_repository}/builds'

    def __call__(self):
        branch = self.config.get('branch', 'master')
        resp = requests.get(self.URL.format(**self.config))
        builds = resp.json()
        onbranch = filter(lambda x: x['branch'] == branch, builds)
        finished = filter(lambda x: x['state'] == 'finished', onbranch)
        if len(list(finished)) == 0:
            raise StopRelease(
                'Travis has not built branch "{0}" yet.'.format(branch))
        latest = finished[0]
        if latest['result'] == 0:
            print('No problem in latest Travis build: "{0}"'.format(
                latest.get('message')))
        else:
            raise StopRelease(
                'Last Travis build on branch "{0}" failed.'.format(branch))


class SetVersionNumberInteractively(ReleaseStep):
    '''Asks the user for the new version number and writes it onto
    the configured source code file.
    '''
    ERROR_CODE = 4

    def __call__(self):
        releaser = self.releaser
        path = releaser.config['version_file']
        releaser.old_version = version_in_python_source_file(path)
        print('Current version: {0}'.format(releaser.old_version))
        releaser.the_version = input('What is the new version number? ')
        # Write the new version onto the source code
        version_in_python_source_file(path, replace=releaser.the_version)


class SetFutureVersion(ReleaseStep):
    '''Replaces the version number in the configured source code file with
    the future version number (the one ending in 'dev').
    '''
    def __call__(self):
        releaser = self.releaser
        path = releaser.config['version_file']
        # If the SetVersionNumberInteractively step is disabled for debugging,
        # we can still execute the current step, by populating the_version:
        if releaser.the_version is None:
            releaser._the_version = version_in_python_source_file(path)
        print('Ready for the next development cycle! Setting version ' +
              releaser.future_version)
        version_in_python_source_file(path, replace=releaser.future_version)

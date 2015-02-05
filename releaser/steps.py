# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import requests
from bag.check_rst import check_rst_file
from bag.console import bool_input
from nine import filter, input, nine
from path import path as pathpy  # TODO Switch to pathlib
from . import ReleaseStep, StopRelease, CommandStep
from .regex import version_in_python_source_file

__all__ = ('Shell', 'CheckRstFiles', 'InteractivelyApproveDistribution',
     'InteractivelyEnsureChangesDocumented', 'CheckTravis',
    'SetVersionNumberInteractively', 'PypiRegister', 'PypiUpload',
    'SetFutureVersion', 'ErrorStep')


@nine
class Shell(ReleaseStep):
    '''Runs some shell command.'''
    ERROR_CODE = 2

    def __init__(self, command, stop_on_failure=True):
        self.COMMAND = command
        self.stop_on_failure = stop_on_failure
        self.no_rollback = 'Unable to roll back the step {0}'.format(self)

    def __call__(self):
        self._execute_or_complain(self.COMMAND)  # sets self.success

    def __str__(self):
        return '[' + self.COMMAND + ']'


class CheckRstFiles(ReleaseStep):
    '''Helps keep documentation correct by verifying .rst documentation files.
    If files are not provided to the constructor, recursively finds *.rst files
    in the current directory and subdirectories.
    '''
    ERROR_CODE = 4

    def __init__(self, *files):
        self.paths = files

    def __call__(self):
        paths = self.paths or pathpy('.').walkfiles('*.rst')
        for path in paths:
            self.log.info('Checking ' + path)
            warnings = check_rst_file(path)
            if warnings:
                raise StopRelease('There are errors in {0}:\n{1}'.format(path,
                    '\n'.join([str(w) for w in warnings])))


class InteractivelyApproveDistribution(ReleaseStep):
    '''Generate a source distribution and let the user verify that
    all files are in there.
    '''
    ERROR_CODE = 5

    def __call__(self):
        self._execute_or_complain('python setup.py sdist')
        # TODO: Optionally xdg-open the archive for convenience
        # Create the sdist with "-d <output_dir>"  on a temp dir.
        # Delete it at the end.
        print("A temporary source distribution has been generated. This is")
        print("your chance to open the new archive (in the 'dist' directory)")
        print("and check that all files are in there.")
        if not bool_input("Do you approve the archive contents?"):
            raise StopRelease('Source distribution content not approved.\n'
                'If the distribution is missing some files,\n'
                "try correcting your MANIFEST.in file according to\n"
                "http://docs.python.org/3/distutils/sourcedist.html"
                "#specifying-the-files-to-distribute")


class InteractivelyEnsureChangesDocumented(ReleaseStep):
    ERROR_CODE = 3

    def __call__(self):
        if bool_input('Did you remember to update the CHANGES file?'):
            self.log.debug('User says CHANGES file is up to date.')
        else:
            raise StopRelease('One more joshlabotniked release is avoided.')


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
        finished = list(filter(lambda x: x['state'] == 'finished', onbranch))
        if len(finished) == 0:
            raise StopRelease(
                'Travis has not built branch "{0}" yet.'.format(branch))
        latest = finished[0]
        if latest['result'] == 0:
            self.log.info('No problem in latest Travis build: "{0}"'.format(
                          latest.get('message')))
            self._succeed()
        else:
            raise StopRelease(
                'Last Travis build on branch "{0}" failed.'.format(branch))


class SetVersionNumberInteractively(ReleaseStep):
    '''Asks the user for the new version number and writes it onto
    the configured source code file.
    '''
    ERROR_CODE = 6

    def __call__(self):
        releaser = self.releaser
        path = releaser.config['version_file']
        keyword = releaser.config.get('version_keyword', 'version')
        releaser.old_version = version_in_python_source_file(
            path, keyword=keyword)
        print('Current version: {0}'.format(releaser.old_version))
        releaser.the_version = input('What is the new version number? ')
        # Write the new version onto the source code
        version_in_python_source_file(
            path, keyword=keyword, replace=releaser.the_version)
        self._succeed()


class PypiRegister(CommandStep):
    COMMAND = 'python setup.py register'
    ERROR_CODE = 7
    no_rollback = 'The release has been created on http://pypi.python.org.\n' \
        'Unfortunately, the release must be removed manually.'

    def _validate_command_output(self, command_output):
        return "Server response (200): OK" in command_output


class PypiUpload(CommandStep):
    COMMAND = 'python setup.py sdist upload'
    ERROR_CODE = 8
    no_rollback = 'Cannot roll back the sdist upload to http://pypi.python.org'

    def _validate_command_output(self, command_output):
        return "Server response (200): OK" in command_output


class SetFutureVersion(ReleaseStep):
    '''Replaces the version number in the configured source code file with
    the future version number (the one ending in 'dev1').
    '''
    ERROR_CODE = 9

    def __call__(self):
        releaser = self.releaser
        path = releaser.config['version_file']
        keyword = releaser.config.get('version_keyword', 'version')
        # If the SetVersionNumberInteractively step is disabled for debugging,
        # we can still execute the current step, by populating the_version:
        if releaser.the_version is None:
            releaser._the_version = version_in_python_source_file(
                path, keyword=keyword)
        self.log.info(
            'Ready for the next development cycle! Setting version '
            + releaser.future_version)
        version_in_python_source_file(
            path, keyword=keyword, replace=releaser.future_version)
        self._succeed()


class ErrorStep(CommandStep):
    '''Raises an exception to force a rollback. Good for testing.'''
    COMMAND = 'thisCommandDontExist'
    ERROR_CODE = 255

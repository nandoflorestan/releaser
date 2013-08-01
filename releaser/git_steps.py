#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from . import ReleaseStep, StopRelease, system, system_or_stop


def get_current_branch():
    with open('.git/HEAD') as f:
        return f.read().strip().split('/')[-1]


class EnsureGitBranch(ReleaseStep):
    '''I must be in the branch specified in config.'''
    ERROR_CODE = 51

    def __call__(self):
        required = self.config.get('branch', 'master')
        branch = get_current_branch()
        if branch != required:
            raise StopRelease('You are in branch "{0}", but should be '
                'in branch "{1}" in order to make a release.'.format(
                    branch, required))


class EnsureGitClean(ReleaseStep):
    '''Ensures we are NOT in a detached head and
    there are no uncommitted changes in tracked files.
    '''
    ERROR_CODE = 52

    def __call__(self):
        code, head = system('git symbolic-ref --quiet HEAD')
        # This returns something like 'refs/heads/master' or nothing.
        # Nothing is bad, indicating a detached head: likely a tag checkout
        if (not head) or code:
            raise StopRelease('Wait, are you on a detached head?')
        code, text = system('git status --short --untracked-files=no')
        if text or code:
            raise StopRelease(
                'There are uncommitted changes in tracked files.')


class GitCommitVersionNumber(ReleaseStep):
    '''Creates a git commit with only one alteration: the new version number.
    Can rollback().
    '''
    COMMAND = 'git commit -a -m "{0}"'
    ERROR_CODE = 53

    def __init__(self, which='the_version', msg="Version {0}",
                 stop_on_failure=True):
        assert which in ('the_version', 'future_version')
        self.which = which
        self.msg = msg.replace('"', '\"')
        self.stop_on_failure = stop_on_failure

    def __call__(self):
        msg = self.msg.format(getattr(self.releaser, self.which))
        cmd = self.COMMAND.format(msg)
        retcode, text = system(cmd)
        if retcode != 0:
            e = 'Error on {0}:\n{1}'.format(msg, text)
            if self.stop_on_failure:
                raise StopRelease(e)
            else:
                print(e)

    def rollback(self):
        retcode, text = system_or_stop('git reset --hard HEAD^')


class GitTag(ReleaseStep):
    '''Tags the current git commit with the new version number. Can rollback().
    '''
    COMMAND = 'git tag -a v{0} -m "Version {0}"'
    ERROR_CODE = 54

    def __call__(self):
        version = self.releaser.the_version
        if version is None:
            print('Skipping the GitTag step. It can only run AFTER some other '
                'step sets *the_version* on the releaser.')
            return
        retcode, text = system(self.COMMAND.format(version))
        if retcode == 0:
            self.releaser.created_tags.append(version)
        else:
            print('The GitTag step failed with the following message:')
            print(text)
            print('Continuing anyway.')

    def rollback(self):
        retcode, text = system_or_stop('git tag -d "v{0}"'.format(
            self.releaser.the_version))


class GitPushTags(ReleaseStep):
    '''Pushes local tags to the remote repository. Can rollback().'''
    COMMAND = 'git push --tags'
    ERROR_CODE = 55
    _success = False

    def __call__(self):
        retcode, text = system(self.COMMAND)
        if retcode == 0:
            self._success = True
        else:
            print('The GitPushTags step failed with the following message:')
            print(text)
            print('Continuing anyway.')

    def rollback(self):
        if not self._success:
            return
        for tag in self.releaser.created_tags:
            retcode, text = system_or_stop(
                'git push --delete origin "v{0}"'.format(tag))

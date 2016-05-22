# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from . import ReleaseStep, CommandStep, StopRelease

__all__ = ('EnsureGitClean', 'EnsureGitBranch',
           'GitCommitVersionNumber', 'GitTag', 'GitPush', 'GitPushTags')


class EnsureGitClean(ReleaseStep):
    """Ensures git state is appropriate to start a release.

    Meaning we are NOT in a detached head and
    there are no uncommitted changes in tracked files.
    """

    ERROR_CODE = 52

    def __call__(self):
        head = self._execute_or_complain('git symbolic-ref --quiet HEAD')
        # This returns something like 'refs/heads/master' or nothing.
        # Nothing is bad, indicating a detached head: likely a tag checkout
        if not head:
            raise StopRelease('Wait, are you on a detached head?')
        changes = self._execute_or_complain(
            'git status --short --untracked-files=no')  # sets self.success
        if changes:
            raise StopRelease(
                'There are uncommitted changes in tracked files.')
        self._succeed()


class EnsureGitBranch(ReleaseStep):
    """I must be in the branch specified in config."""

    ERROR_CODE = 51

    def _get_current_branch(self):
        branch = self._execute_or_complain('git rev-parse --abbrev-ref HEAD')
        return None if branch == 'HEAD' else branch

    def __call__(self):
        required = self.config.get('branch', 'master')
        branch = self._get_current_branch()
        if branch != required:
            raise StopRelease(
                'You are in branch "{0}", but should be '
                'in branch "{1}" in order to make a release.'.format(
                    branch, required))
        self._succeed()


class GitCommitVersionNumber(ReleaseStep):
    """Creates a git commit with only one alteration: the new version number.

    Can rollback().
    """

    COMMAND = 'git commit -a -m "{0}"'
    ERROR_CODE = 53

    def __init__(self, which='the_version', msg='Version {0}',
                 stop_on_failure=True):
        assert which in ('the_version', 'future_version')
        self.which = which
        self.msg = msg.replace('"', '\"')  # escape quotes for shell
        self.stop_on_failure = stop_on_failure

    def __call__(self):
        msg = self.msg.format(getattr(self.releaser, self.which))
        self._execute_or_complain(self.COMMAND.format(msg))  # sets success

    def rollback(self):
        self._execute_or_complain('git reset --hard HEAD^')


class GitTag(ReleaseStep):
    """Tags the current git commit with the new version number.

    Can rollback().
    """

    COMMAND = 'git tag -a v{0} -m "Version {0}"'
    ERROR_CODE = 54
    stop_on_failure = False

    def __call__(self):
        version = self.releaser.the_version
        if version is None:
            self.log.warning('Skipping the GitTag step. It can only run AFTER '
                'some other step sets *the_version* on the releaser.')
            return
        self._execute_or_complain(self.COMMAND.format(version))  # sets success
        if self.success:
            self.releaser.created_tags.append(version)

    def rollback(self):
        self._execute_or_complain('git tag -d "v{0}"'.format(
            self.releaser.the_version))


class GitPush(ReleaseStep):
    """Does ``git push``. This critical step has no rollback."""

    COMMAND = 'git push'
    ERROR_CODE = 55
    stop_on_failure = False  # It should be easy to 'git push' afterwards
    no_rollback = 'One should never try to undo a git push. Really.\n' \
        'This release process went far -- the push succeeded -- but\n' \
        'something else went wrong after the push. I figure it will\n' \
        'be easier for you to finish the release process manually,\n' \
        'so I will NOT roll back any of the steps that preceded the push.'

    def __call__(self):
        self._execute_or_complain(self.COMMAND)  # sets success
        if self.success:
            # Erase history so all steps before the push won't be rolled back
            self.log.debug('GitPush successful; erasing rollback history.')
            # self.releaser.rewindable.clear()
            self.releaser.rewindable[:] = []  # Python 2.6 has no clear()
            # self.releaser.non_rewindable.clear()
            self.releaser.non_rewindable[:] = []  # Python 2.6 has no clear()


class GitPushTags(CommandStep):
    """Pushes local tags to the remote repository. Can rollback()."""

    COMMAND = 'git push --tags'
    ERROR_CODE = 56
    stop_on_failure = False

    def rollback(self):
        for tag in self.releaser.created_tags:
            self._execute_or_complain(
                'git push --delete origin "v{0}"'.format(tag))

#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Script that releases a new version of the software.'''

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from releaser import Releaser          # easy_install -UZ releaser
from releaser.steps import (Shell, CheckTravis, SetFutureVersion,
    InteractivelyApproveDistribution, SetVersionNumberInteractively)
from releaser.git_steps import (EnsureGitClean, EnsureGitBranch,
    GitCommitVersionNumber, GitTag, PypiRegister, PypiUpload,
    GitPush, GitPushTags)

# This config information is used by multiple release steps below.
config = dict(
    github_user='nandoflorestan',  # TODO infer from .git/config
    github_repository='releaser',
    branch='master',  # Only release new versions in this git branch
    changes_file='CHANGES.rst',
    version_file='setup.py',  # Read and write version number on this file
    log_file='release.log.utf-8.tmp',
    verbosity='info',  # debug | info | warn | error
)

# You can customize your release process below.
# Comment out any steps you don't desire and add your own steps.
Releaser(config,
    Shell('python setup.py test'),  # First of all ensure tests pass
    # TODO IMPLEMENT CompileAndVerifyTranslations,
    # TODO IMPLEMENT BuildSphinxDocumentation,
    # TODO IMPLEMENT Tell the user to upload the built docs (give URL)
    EnsureGitClean,  # There are no uncommitted changes in tracked files.
    EnsureGitBranch,  # I must be in the branch specified in config
    InteractivelyApproveDistribution,  # Generate sdist, let user verify it
    # CheckTravis,  # We run this late, so travis-ci has more time to build

    # ==========  All checks pass. RELEASE!  ==========
    SetVersionNumberInteractively,  # Ask for version and write to source code
    # TODO IMPLEMENT CHANGES file: add heading for current version (below dev)
    GitCommitVersionNumber,
    GitTag,  # Locally tag the current commit with the new version number
    PypiRegister,  # Creates the new release at http://pypi.python.org
    PypiUpload,  # Uploads a source distribution to http://pypi.python.org

    # ==========  Post-release: adjust repositories for new dev ==========
    SetFutureVersion,  # Writes incremented version, now with 'dev' suffix
    GitCommitVersionNumber('future_version', msg='Bump version after release'),
    GitPush,  # Cannot be undone. If successful, previous steps won't roll back
    GitPushTags,
).release()

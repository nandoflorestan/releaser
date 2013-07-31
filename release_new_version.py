#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Script that releases a new version of the software.'''

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from release import Releaser  # https://pypi.python.org/pypi/release
from release.steps import (Shell, CheckTravis, SetFutureVersion,
    InteractivelyApproveDistribution, SetVersionNumberInteractively)
from release.git_steps import (EnsureGitClean, EnsureGitBranch,
    GitCommitVersionNumber, GitTag, GitPushTags)

# This config information is used by multiple release steps below.
config = dict(
    github_user='nandoflorestan',  # TODO infer from .git/config
    github_repository='release',
    branch='master',  # Only release new versions in this git branch
    changes_file='CHANGES.rst',
    version_file='setup.py',  # Read and write version number on this file
)

# You can customize your release process below.
# Comment out any steps you don't desire and add your own steps.
Releaser(config,
    # First of all we execute our tests and stop if any of them fail:
    Shell('python setup.py test'),
    # TODO IMPLEMENT CompileAndVerifyTranslations,
    # TODO IMPLEMENT BuildSphinxDocumentation(config),
    # TODO IMPLEMENT Tell the user to upload the built docs (give URL)
    EnsureGitClean,  # There are no uncommitted changes in tracked files.
    EnsureGitBranch,  # I must be in the branch specified in config
    # TODO IMPLEMENT Check CHANGES file for the current milestone
    InteractivelyApproveDistribution,  # Generate sdist, let user verify it
    CheckTravis,  # We run this late, so Travis has more time to build
    # ========== All checks pass. Let's do this! ==========
    SetVersionNumberInteractively,  # Ask for version and write to source code
    Shell('python setup.py register sdist upload'),  # http://pypi.python.org
    GitCommitVersionNumber,
    GitTag,  # Locally tag the current commit with the new version number
    SetFutureVersion,  # Write incremented version, now with 'dev' suffix
    GitCommitVersionNumber('future_version', msg='Bump version after release'),
    # git push is the ONLY thing that absolutely cannot be undone:
    Shell('git push', stop_on_failure=False),
    GitPushTags,
).release()

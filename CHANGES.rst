================
Breaking changes
================

Version 2.0.0
=============

When you upgrade to this version you need to reposition 2 build steps.

**releaser** now uses **twine** to upload packages to pypi. There is no longer
a need to build a test package before releasing. So these 2 steps which were
preparation steps::

    InteractivelyApproveDistribution,  # Generate sdist, let user verify it
    InteractivelyApproveWheel,         # Generate wheel, let user verify it

…are now expected to appear in the RELEASE (middle) part of your script.
Move them down in the list of steps.  In 1.x these steps built a
test package; in 2.x they build the actual package that will be uploaded
to pypi.

Refer to our updated `example script`_.
.. _`example script`: https://raw.github.com/nandoflorestan/releaser/master/release_new_version.py

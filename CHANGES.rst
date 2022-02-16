================
Breaking changes
================


Version 3.0.0 (2022-02)
=======================

The scene has changed; pip is no longer king, poetry delivers a better experience
with much less confusion when packaging a library or project.  PEPs 517 and 518 replace
the old setup.py file with the new pyproject.toml.

We now adapt to all this, keeping compatibility with the old way.

- The InteractivelyApproveDistribution and InteractivelyApproveWheel commands are no more,
  having been replaced by a single InteractivelyApprovePackage which confirms only once,
  after one or two shell commands build the sdist and wheel -- see our
  example ``release_new_version.py`` for details.
- PypiUpload command has been renamed to TwineUploadSource; but if you use poetry you
  don't need Twine, since poetry can upload.
- PypiUploadWheel has been renamed to TwineUploadWheel; but if you use poetry you
  shouldn't use this, since you can just do ``poetry publish``.


Version 2.0.0 (2021-02)
=======================

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

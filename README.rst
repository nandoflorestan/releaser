Easily write a script to release a new version, with variable steps.
====================================================================

Releasing software usually is a pain. There are several checks that
the developer must make for each new version. The developer is prone
to forget one of them or perform the checks out of the optimal order.
As Murphy would have it, many buggy releases are created for this reason.

*releaser* is a little framework the developer can use to write a script to
guide him through the new version release process, such that the checks
are performed automatically. (Each software project will have
a release script that differs a little bit from others.)

Many steps of a common release process have already been implemented,
and you can easily write your own.
(If you do write a step, please donate the code to the project.)

Installing *releaser*
=====================

Activate your virtualenv, then:

    easy_install -UZ releaser

Getting started
===============

Simply `download this script`_ to the root of your project, then edit it.
(You can `read it here`_.)

Links
=====

Our project home and issue tracker are at GitHub_.
It's easy to `use the source`_.

*releaser* supports Python 2.6, 2.7, 3.2 and 3.3 (without translation)
through the nine_ project.

A popular alternative to *releaser* is the project `zest.releaser`_.

.. _`download this script`: https://github.com/nandoflorestan/releaser/raw/master/release_new_version.py
.. _`read it here`: https://github.com/nandoflorestan/releaser/blob/master/release_new_version.py
.. _GitHub: https://github.com/nandoflorestan/releaser
.. _`use the source`: https://github.com/nandoflorestan/releaser/tree/master/releaser
.. _nine: https://pypi.python.org/pypi/nine
.. _`zest.releaser`: https://pypi.python.org/pypi/zest.releaser

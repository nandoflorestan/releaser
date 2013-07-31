Easily write a script to release a new version, with variable steps.
====================================================================

Releasing software usually is a pain. There are several checks that
the developer must make for each new version. The developer is prone
to forget one of them or perform the checks out of the optimal order.
As Murphy would have it, many buggy releases are created for this reason.

*release* is a little framework the developer can use to write a script to
guide him through the new version release process, such that the checks
are performed automatically. (Each software project will have
a release script that differs a little bit from others.)

Many steps of a common release process have already been implemented,
and you can easily write your own.
(If you do write a step, please donate the code to the project.)

*release* supports Python 2 and Python 3 through the nine_ project.

You may want to take a look at another project, too: `zest.releaser`_.

.. _nine: https://pypi.python.org/pypi/nine
.. _`zest.releaser`: https://pypi.python.org/pypi/zest.releaser

====================================================================
Easily write a script to release a new version, with variable steps.
====================================================================

Releasing software is a painful process. There are several checks that
the developer must make for each new version. The developer is prone
to forget one of them or perform the checks out of the optimal order.
As Murphy would have it, many buggy releases are created for this reason.

*releaser* is a little framework the developer can use to write a script to
guide him through the new version release process, such that many checks
are performed automatically. (Each software project will have
a release script that differs a little bit from others.)

Now that I use *releaser* I can release my Python libraries more quickly and
easily, so I find that I release more often. Well worth the initial investment.

Many steps of a common Python release process have already been implemented,
and you can easily write your own. If you do write a step, please donate it
to the project by making a pull request on GitHub_.


Installing *releaser*
=====================

Activate your virtualenv, then::

    easy_install -UZ releaser


Getting started
===============

Simply `download this script`_ to the root of your project::

    curl -O https://raw.github.com/nandoflorestan/releaser/master/release_new_version.py
    chmod +x ./release_new_version.py
    git add release_new_version.py

Then edit the script as necessary. (You can `read it here`_.)

When you execute the script, the configured steps are executed in order. The
screen shows little information, but you have all details in the log file.

Some of the steps are interactive; for instance, you may be asked to
verify the contents of a zip or wheel file before it is uploaded to pypi_.
*releaser* also makes you type the number of the version being released, which
is then validated (for instance, it is compared to the current version), then
written to a source code file that belongs to your project.


Rolling back
============

If any one of the steps fails, *releaser* asks you whether you would like it to
rewind the process. (Yes, you get to decide.) How does this work?

A few of the steps (especially those involving git) have a rollback() method.
For other steps (especially those that just check things at the beginning)
rewinding wouldn't make any sense since they don't leave durable artifacts.

If your steps are correctly configured, rolling back leaves you exactly as you
were before *releaser* ran. But:

Note the GitPush step has special behaviour. When it executes successfully
but an error occurs in a later step, *releaser* decides NOT to roll back
GitPush and the steps that preceded it. This is because one cannot
delete git history once it has been pushed to a public server and
GitPush tends to be one of the last steps anyway, so it is easier to
finish the release manually than to deal with git history inconsistencies.

Other steps (such as creating a release on pypi_) cannot be automatically
rewinded for technical reasons, but *releaser* warns you that you have to
do it manually before asking whether to roll back the release.


Links
=====

Our project home and issue tracker are at GitHub_.
It's easy to `read the source code`_.

A popular alternative to *releaser* is the project `zest.releaser`_. It differs
in features, manners of extensibility and support for Python versions.

*releaser* supports Python 2.6, 2.7, 3.2, 3.3, 3.4 and 3.5 (without translation)
through the nine_ project.

.. _`download this script`: https://raw.github.com/nandoflorestan/releaser/master/release_new_version.py
.. _`read it here`: https://github.com/nandoflorestan/releaser/blob/master/release_new_version.py
.. _pypi: https://pypi.python.org/pypi
.. _GitHub: https://github.com/nandoflorestan/releaser
.. _`read the source code`: https://github.com/nandoflorestan/releaser/tree/master/releaser
.. _nine: https://pypi.python.org/pypi/nine
.. _`zest.releaser`: https://pypi.python.org/pypi/zest.releaser

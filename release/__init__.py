# -*- coding: utf-8 -*-

'''Framework for releasing Python software with variable steps in the
release process.
'''

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import subprocess
from sys import platform
from pkg_resources import parse_version
from .regex import error_in_version
# TODO logging instead of printing


class StopRelease(Exception):
    '''Release steps should raise this exception to stop the whole program.'''
    def __init__(self, msg):
        self.msg = msg


class ReleaseStep(object):
    '''Abstract base class for release steps.'''
    def __call__(self):
        '''Override this method to do the main work of the release step.
        On error, StopRelease should be raised. On success, this method can
        return a warning unicode string. Or nothing.
        '''
        raise StopRelease('Step not implemented.')

    def perform(self):
        '''Wraps the call to this step, prints the warning if one is returned,
        and exits if StopRelease is raised.
        '''
        try:
            warning = self()
        except StopRelease as e:
            print('Release process stopped at step {0}:'.format(
                  type(self)))
            print(e.msg)
            from sys import exit
            exit(self.ERROR_CODE)
        if warning:
            print(type(self), '\t', warning)

    def rollback(self):
        '''Rewind this command, when applicable.'''
        pass

    ERROR_CODE = 1


def system(command, input='', shell=True):
    p = subprocess.Popen(command, shell=shell,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         close_fds=not platform.startswith('win'))
    i, o, e = (p.stdin, p.stdout, p.stderr)
    if input:
        i.write(input)
    i.close()
    return_code = p.wait()
    result = o.read() + e.read()
    o.close()
    e.close()
    # TODO: If not verbose, do not print result
    if result:
        print(result.decode('utf-8'))
    return return_code, result


def system_or_stop(command):
    return_code, text = system(command)
    if return_code != 0:
        raise StopRelease('Command failed with code {0}: {1}'.format(
            return_code, command))
    return text


class Releaser(object):
    def __init__(self, config, *steps):
        self.config = config
        # First, convert steps provided by the user into real instances
        self.instances = []
        self.created_tags = []
        for step in steps:
            if isinstance(step, type):
                step = step()  # Instantiate the ReleaseStep subclass
            step.config = config
            step.releaser = self
            self.instances.append(step)
        # Now that all steps are correctly instantiated,
        # it is safe to start running them by calling release().

    def release(self):
        # TODO: Rollback support
        for step in self.instances:
            step.perform()
        print('Successfully released {0}. Sorry for the convenience, mcdonc!'
              .format(self.the_version))

    old_version = None     # 0.1.2dev (exists when the program starts)
    _the_version = None    # 0.1.2    (the version being released)

    @property
    def the_version(self):
        return self._the_version

    @the_version.setter
    def the_version(self, val):
        val = val.strip()
        e = error_in_version(val, allow_dev=False)
        if e:
            raise StopRelease(e)
        if parse_version(self.old_version) >= parse_version(val):
            raise StopRelease(
                'No, the version number must be higher than the current one!')
        self._the_version = val

    @property
    def future_version(self):
        parts = self.the_version.split('.')
        parts[-1] = str(int(parts[-1]) + 1)
        return '.'.join(parts) + 'dev'

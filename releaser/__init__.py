# -*- coding: utf-8 -*-

'''Framework for releasing Python software with variable steps in the
release process.
'''

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import subprocess
from sys import platform
from pkg_resources import parse_version
from bag.log import setup_log
from .regex import error_in_version


class StopRelease(RuntimeError):
    '''Release steps should raise this exception to stop the whole program.'''


class ReleaseStep(object):
    '''Abstract base class for release steps.'''
    ERROR_CODE = 1
    success = None
    stop_on_failure = True

    def __call__(self):
        '''Override this method to do the main work of the release step.
        On error, StopRelease should be raised.
        '''
        raise StopRelease('Step not implemented.')

    def _succeed(self):
        self.success = True

    def _fail(self, msg):
        self.success = False
        if self.stop_on_failure:
            raise StopRelease(msg)
        else:
            self.log.warning(msg + '\nContinuing anyway.')

    def _execute(self, command, input='', shell=True):
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
        normal_output = o.read().decode('utf-8')
        error_output = e.read().decode('utf-8')
        o.close()
        e.close()
        self.log.debug(normal_output)
        self.log.error(error_output)
        return return_code, normal_output + error_output

    def _execute_or_complain(self, command, input='', shell=True,
            msg='Command failed with code {code}: {cmd}'):
        return_code, text = self._execute(command)
        if return_code == 0:
            self._succeed()
        else:
            self._fail(msg.format(code=return_code, cmd=command))
        return text


class Releaser(object):
    def __init__(self, config, *steps):
        self.created_tags = []
        self.config = config
        # Configure logging
        path = config.get('log_file', 'release.log.utf-8.tmp')
        screen_level = config.get('verbosity', 'info')
        self.log = setup_log(path=path, rotating=False, file_mode='w',
                             disk_level='debug', screen_level=screen_level)
        # Convert steps provided by the user into real instances
        self.instances = []
        for step in steps:
            if isinstance(step, type):
                step = step()  # Instantiate the ReleaseStep subclass
            step.config = config
            step.releaser = self
            step.log = self.log
            self.instances.append(step)
        # Now that all steps are correctly instantiated,
        # it is safe to start running them by calling release().

    def release(self):
        rewindable = []
        for step in self.instances:
            step_name = type(step).__name__
            self.log.info('\n===========  ' + step_name + '  ===========')
            try:
                step()
            except StopRelease as e:
                self.log.critical('Release process stopped at step {0}:\n{1}'
                    .format(step_name, str(e)))
                self.rewind(rewindable)
                from sys import exit
                exit(step.ERROR_CODE)
            except Exception:
                self.rewind(rewindable)
                raise
            else:
                if step.success and hasattr(step, 'rollback'):
                    rewindable.append(step)
        self.log.info('Successfully released version {0}. '
            'Sorry for the convenience, mcdonc!'.format(self.the_version))

    def rewind(self, steps):
        self.log.critical('\n****************  ROLLBACK  ****************')
        steps.reverse()
        for step in steps:
            step_name = type(step).__name__
            self.log.critical('\n===========  ROLLBACK {0}  ==========='
                              .format(step_name))
            try:
                step.rollback()
            except Exception as e:
                self.log.error('Could not roll back step {0}:\n{1}'
                    .format(step_name, str(e)))

    _old_version = None    # 0.1.2dev (exists when the program starts)
    _the_version = None    # 0.1.2    (the version being released)

    @property
    def old_version(self):
        return self._old_version

    @old_version.setter
    def old_version(self, val):
        self._old_version = val
        self.log.debug('Old version: {0}'.format(val))

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
        self.log.debug('Version being released: {0}'.format(val))

    @property
    def future_version(self):  # 0.1.3dev (development version after release)
        parts = self.the_version.split('.')
        parts[-1] = str(int(parts[-1]) + 1)
        return '.'.join(parts) + 'dev'

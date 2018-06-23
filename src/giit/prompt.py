import os
import subprocess
import time
import logging

from . import compat
from . import check_output
from . import run_result
from . import run_error


class Prompt(object):

    def __init__(self, cwd=None, env=None, stdout=None, stderr=None, log=None):

        self.cwd = cwd if cwd else os.getcwd()
        self.env = env if env else dict(os.environ)
        self.stdout = stdout if stdout else subprocess.PIPE
        self.stderr = stderr if stderr else subprocess.PIPE
        self.log = log if log else logging.getLogger(__name__)

    def run(self, command, **kwargs):
        """Runs the command
        :param command: String or list of arguments
        :param kwargs: Keyword arguments passed to Popen(...)
        :return: A RunResult object representing the result of the command
        """

        if isinstance(command, compat.string_type):
            kwargs['shell'] = True

        if 'env' not in kwargs:
            kwargs['env'] = self.env

        if 'stdout' not in kwargs:
            kwargs['stdout'] = self.stdout

        if 'stderr' not in kwargs:
            kwargs['stderr'] = self.stderr

        if 'cwd' not in kwargs:
            kwargs['cwd'] = self.cwd

        self.log.debug("command=%s, cwd=%s", command, kwargs['cwd'])

        start_time = time.time()

        popen = subprocess.Popen(
            command,
            # Need to decode the stdout and stderr with the correct
            # character encoding (http://stackoverflow.com/a/28996987)
            universal_newlines=True,
            **kwargs)

        stdout, stderr = popen.communicate()

        end_time = time.time()

        if isinstance(command, list):
            command = ' '.join(command)

        result = run_result.RunResult(
            command=command, path=kwargs['cwd'],
            stdout=stdout, stderr=stderr, returncode=popen.returncode,
            time=end_time - start_time, env=kwargs['env'])

        if popen.returncode != 0:
            raise run_error.RunError(result)

        return result

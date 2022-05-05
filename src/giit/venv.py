#!/usr/bin/env python
# encoding: utf-8

import os
import sys


class VirtualEnv(object):
    """Simple object which can be used to work within a virtualenv.


    venv = VirtualEnv.create(cwd='/tmp', runner=command.run, name=None)

    It is important to be aware of the cwd parameter, e.g. if you access files
    etc. it will be relative to cwd. So if cwd is the 'build' directory and you
    access a file in the root of the repository it will need to be prefixed
    with '../somefile.txt'.
    """

    def __init__(self, prompt, log):

        self.prompt = prompt
        self.log = log

    def create_environment(self, path):

        if not os.path.isdir(path):

            args = ["python", "-m", "venv", path]

            self.prompt.run(command=args)

        # Create a new environment based on the new virtualenv
        env = dict(os.environ)

        # Make sure the virtualenv Python executable is first in PATH
        if sys.platform == "win32":
            python_path = os.path.join(path, "Scripts")
        else:
            python_path = os.path.join(path, "bin")

        env["PATH"] = os.path.pathsep.join([python_path, env["PATH"]])

        return env


class NameToPathAdapter(object):
    def __init__(self, virtualenv, virtualenv_root_path):
        self.virtualenv = virtualenv
        self.virtualenv_root_path = virtualenv_root_path

    def create_environment(self, name):

        path = os.path.join(self.virtualenv_root_path, name)

        return self.virtualenv.create_environment(path=path)

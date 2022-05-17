#!/usr/bin/env python
# encoding: utf-8

import os
import sys


class VirtualEnv(object):
    """Simple object which can be used to work within a virtualenv."""

    def __init__(self, prompt, log):

        self.prompt = prompt
        self.log = log

    def create_environment(self, path):

        if not os.path.isdir(path):

            self.prompt.run(command=["python", "-m", "virtualenv", path])

        # Create a new environment based on the new virtualenv
        env = dict(os.environ)

        # Make sure the virtualenv Python executable is first in PATH
        if sys.platform == "win32":
            python_path = os.path.join(path, "Scripts")
        else:
            python_path = os.path.join(path, "bin")

        env["PATH"] = os.path.pathsep.join([python_path, env["PATH"]])

        return env

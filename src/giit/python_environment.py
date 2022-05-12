#!/usr/bin/env python
# encoding: utf-8

import sys
import hashlib
import os
import json


class PythonEnvironment(object):
    def __init__(self, prompt, virtual_environment, log):
        """Create new environments for running python commands.

        Essentially, if needed, we just create a virtual
        environment and modify the path such that it is
        found before any system packages.

        :param prompt: A Prompt object
        :param virtual_environment: A Virtual Envionment object
        :param log: A log object
        """
        self.prompt = prompt
        self.virtual_environment = virtual_environment
        self.log = log

    def from_requirements(self, requirements, pip_packages):
        """Create an environment from a requirements file.

        :param requirements: Path to the requirements
        """
        if requirements is None and pip_packages is None:
            return self.from_system()

        name = self._environment_name(
            requirements=requirements, pip_packages=pip_packages
        )

        env = self.virtual_environment.create_environment(name=name)

        # We use the -U (--upgrade) to pip since otherwise it will
        # not update to the newest version available. Also when
        # installing via VCS such as git
        # (https://pip.pypa.io/en/latest/reference/pip_install/#vcs-support)
        # we won't get the newest available version.

        if requirements:
            # Install the requirements
            command = "python -m pip install -U -r {}".format(requirements)
            self.prompt.run(command=command, env=env)

        if pip_packages:
            # Install the pip packages
            pip_packages = " ".join(pip_packages)
            command = "python -m pip install -U {}".format(pip_packages)

            self.prompt.run(command=command, env=env)

        return env

    def from_system(self):
        """:return: The default environment."""
        return dict(os.environ)

    def _environment_name(self, requirements, pip_packages):
        """Create an unique name for the environment."""

        # Read the contents of the requirements file, to ensure we
        # generate a new environment if it changes
        if requirements:
            with open(requirements, "r") as f:
                requirements_content = f.read()
        else:
            requirements_content = ""

        # We need to make a hashable name
        info = json.dumps(
            {"requirements": requirements_content, "pip_packages": pip_packages}
        )

        # The Python executable
        python = sys.executable
        python_hash = hashlib.sha1(python.encode("utf-8")).hexdigest()[:6]

        # The requirements
        info_hash = hashlib.sha1(info.encode("utf-8")).hexdigest()[:6]

        name = "giit-virtualenv-" + info_hash + "-" + python_hash

        return name

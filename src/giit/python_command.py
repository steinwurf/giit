#! /usr/bin/env python
# encoding: utf-8

import os
import sys
import hashlib

import giit.config_reader


class PythonCommand(object):

    def __init__(self, config, environment, prompt, log):
        """
        :param config: A PythonConfig object
        """
        self.config = config
        self.environment = environment
        self.prompt = prompt
        self.log = log

    def run(self, context):

        self.log.debug("context=%s", context)

        reader = giit.config_reader.ConfigReader(
            config=self.config, context=context)

        # We might try to access a requirements.txt file in the
        # repository here. This may fail on older tags etc. and
        # that is OK if allow_failure is true
        try:
            env = self.environment.from_requirements(
                requirements=reader.requirements,
                pip_packages=reader.pip_packages)

            for script in reader.scripts:
                self.log.info('Python: %s', script)
                self.prompt.run(command=script, cwd=reader.cwd,
                                env=env)

        except Exception:

            if reader.allow_failure:
                self.log.exception('PythonCommand')
            else:
                raise

#! /usr/bin/env python
# encoding: utf-8

import os
import sys
import hashlib

import giit.python_config


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

        # Expand the context in the config
        self.config = giit.python_config.fill_dict(
            context=context, config=self.config)

        self.log.debug("context=%s", context)
        self.log.debug("config=%s", self.config)

        # We might try to access a requirements.txt file in the
        # repository here. This may fail on older tags etc. and
        # that is OK if allow_failure is true
        try:
            env = self.environment.from_requirements(
                requirements=self.config['requirements'],
                pip_packages=self.config['pip_packages'])

            if self.config["python_path"]:
                if 'PYTHONPATH' in env:
                    env['PYTHONPATH'] = os.path.pathsep.join(
                        [self.config["python_path"], env['PYTHONPATH']])
                else:
                    env['PYTHONPATH'] = self.config["python_path"]

            for script in self.config["scripts"]:
                self.log.info('Python: %s', script)
                self.prompt.run(command=script, cwd=self.config["cwd"],
                                env=env)

        except Exception:

            if self.config["allow_failure"]:
                self.log.exception('PythonCommand')
            else:
                raise

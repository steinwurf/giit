#!/usr/bin/env python
# encoding: utf-8

import os


class PythonCommand(object):
    def __init__(self, environment, prompt, log):
        """
        :param config: A PythonConfig object
        """
        self.environment = environment
        self.prompt = prompt
        self.log = log

    def run(self, config):

        self.log.debug("config_without_context =%s", config)

        # Expand the context in the config. The config/command is shared
        # between all the tasks generated.
        # self.config = giit.config.fill_dict(
        #     context=context, config=self.config)

        # self.log.debug("context=%s", context)
        self.log.debug("config_with_context =%s", config)

        # We might try to access a requirements.txt file in the
        # repository here. This may fail on older tags etc. and
        # that is OK if allow_failure is true
        try:
            env = self.environment.from_requirements(
                requirements=config["requirements"], pip_packages=config["pip_packages"]
            )

            if config["python_path"]:
                if "PYTHONPATH" in env:
                    env["PYTHONPATH"] = os.path.pathsep.join(
                        [config["python_path"], env["PYTHONPATH"]]
                    )
                else:
                    env["PYTHONPATH"] = config["python_path"]

            for script in config["scripts"]:
                self.log.info("Python: %s", script)
                self.prompt.run(command=script, cwd=config["cwd"], env=env)

        except Exception:

            if config["allow_failure"]:
                self.log.exception("PythonCommand")
            else:
                raise

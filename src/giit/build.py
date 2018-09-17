import click
import tempfile
import hashlib
import os
import logging
import json
import sys
import shutil

import giit.logs
import giit.giit_json


class Build(object):

    def __init__(self, step,
                 repository,
                 factory,
                 build_path=None,
                 giit_path=None,
                 config_path=None,
                 config_branch=None,
                 verbose=False):

        self.step = step
        self.repository = repository
        self.factory = factory
        self.build_path = build_path
        self.giit_path = giit_path
        self.config_path = config_path
        self.config_branch = config_branch
        self.verbose = verbose

    def run(self):

        # Setup giit data path
        if not self.giit_path:
            self.giit_path = os.path.join(
                tempfile.gettempdir(), 'giit', 'data')

        if not os.path.isdir(self.giit_path):
            os.makedirs(self.giit_path)

        # Setup logging
        giit.logs.setup_logging(
            giit_path=self.giit_path, verbose=self.verbose)

        # Create the build build log
        log = logging.getLogger('giit.main')

        # Add details to log file
        log.debug('build_path=%s', self.build_path)
        log.debug('giit_path=%s', self.giit_path)
        log.debug('config_branch=%s', self.config_branch)
        log.debug('config_path=%s', self.config_path)

        log.info('Lets go: %s', self.step)

        # Resolve the repository
        factory = self.factory.resolve_factory(
            giit_path=self.giit_path, repository=self.repository)

        git_repository = factory.build()

        # Set the build path
        if not self.build_path:
            self.build_path = os.path.join(
                self.giit_path, 'build', git_repository.unique_name())

        # If the step is clean we do it without fetching or cloning
        if self.step == 'clean':

            log.info("Cleaning: %s", self.build_path)

            if os.path.isdir(self.build_path):
                shutil.rmtree(self.build_path, ignore_errors=True)

            return

        # Make sure the build directory exists
        if not os.path.isdir(self.build_path):
            os.makedirs(self.build_path)

        log.info("Building into: %s", self.build_path)

        # Make sure the repository is available
        git_repository.clone()

        # Read the 'giit.json'
        json_config = giit.giit_json.GiitJson(git_repository=git_repository,
                                              log=logging.getLogger(
                                                  'giit.giit_json'),
                                              config_path=self.config_path,
                                              config_branch=self.config_branch)

        config = json_config.read()

        if self.step not in config:
            raise RuntimeError("Error step {} not found in {}".format(
                               self.step, config))

        substep_configs = config[self.step]

        # The sub-steps can be a list
        if not isinstance(substep_configs, list):
            substep_configs = [substep_configs]

        for substep_config in substep_configs:
            self._run_step(config=substep_config,
                           git_repository=git_repository)

    def _run_step(self, config, git_repository):

        log = logging.getLogger('giit.main')

        # Instantiate the cache
        cache_factory = self.factory.cache_factory(
            giit_path=self.giit_path,
            unique_name=git_repository.unique_name())

        cache = cache_factory.build()

        factory = self.factory.build_factory()

        # Provide the different needed by the factory
        factory.provide_value(name='config', value=config)
        factory.provide_value(name='build_path', value=self.build_path)
        factory.provide_value(name='giit_path', value=self.giit_path)
        factory.provide_value(name='git_repository', value=git_repository)

        # Run the command

        with cache:

            task_generator = factory.build()

            tasks = task_generator.tasks()

            for task in tasks:

                log.info("Running task: scope '%s' name '%s'",
                         task.context['scope'], task.context['checkout'])

                task.run()

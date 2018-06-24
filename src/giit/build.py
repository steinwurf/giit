import click
import tempfile
import hashlib
import os
import logging
import json
import sys

import giit.factory


class Build(object):

    def __init__(self, step,
                 repository,
                 build_path=None,
                 data_path=None,
                 json_config=None,
                 source_branch=None):

        self.step = step
        self.repository = repository
        self.build_path = build_path
        self.data_path = data_path
        self.json_config = json_config
        self.source_branch = source_branch

    def run(self):

        # Location for giit files - if not user specified
        giit_path = os.path.join(tempfile.gettempdir(), 'giit')

        # Setup data path
        if not self.data_path:
            self.data_path = os.path.join(giit_path, 'data')

            if not os.path.isdir(self.data_path):
                os.makedirs(self.data_path)

        logger = logging.getLogger('giit')
        logger.setLevel(logging.DEBUG)

        # create file handler which logs even debug messages
        logfile = os.path.join(self.data_path, 'giit.log')
        fh = logging.FileHandler(logfile)
        fh.setLevel(logging.DEBUG)

        # create console handler with a higher log level
        ch = logging.StreamHandler(stream=sys.stdout)
        ch.setLevel(logging.INFO)

        # create formatter and add it to the handlers
        fh_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(fh_formatter)

        ch_formatter = logging.Formatter('%(message)s')
        ch.setFormatter(ch_formatter)

        # add the handlers to the logger
        logger.addHandler(fh)
        logger.addHandler(ch)

        log = logging.getLogger('giit.main')

        # Add details to log file
        log.debug('build_path=%s', self.build_path)
        log.debug('data_path=%s', self.data_path)
        log.debug('json_config=%s', self.json_config)
        log.debug('source_branch=%s', self.source_branch)

        log.info('Lets go!')

        # Resolve the repository
        factory = self.resolve_factory()

        git_repository = factory.build()
        git_repository.clone(repository=self.repository)

        # Set the build path
        if not self.build_path:
            self.build_path = os.path.join(giit_path, 'build',
                                           git_repository.unique_name)

            if not os.path.isdir(self.build_path):
                os.makedirs(self.build_path)

        log.info("Building into: %s", self.build_path)

        # Get the command
        if not self.json_config:
            self.json_config = os.path.join(
                git_repository.repository_path, 'giit.json')

        with open(self.json_config, 'r') as config_file:
            config = json.load(config_file)

        if self.step not in config:
            raise RuntimeError("Error step %s not found in %s",
                               self.step, self.json_config)

        step_config = config[self.step]

        # Instantiate the cache
        cache_factory = self.clone_factory(
            unique_name=git_repository.unique_name)

        cache = cache_factory.build()

        # All steps has a type which controls the available options and
        # actions
        build_type = config[self.step]['type']

        factory = self.build_factory(build_type=build_type)

        # Provide the different needed by the factory
        factory.provide_value(name='config', value=config[self.step])
        factory.provide_value(name='build_path', value=self.build_path)
        factory.provide_value(name='data_path', value=self.data_path)
        factory.provide_value(name='git_repository', value=git_repository)

        # Run the command

        with cache:

            task_generator = factory.build()

            tasks = task_generator.tasks()

            for task in tasks:
                task.run()

    def resolve_factory(self):
        return giit.factory.resolve_factory(
            data_path=self.data_path,
            source_branch=self.source_branch)

    def clone_factory(self, unique_name):
        return giit.factory.cache_factory(
            data_path=self.data_path,
            unique_name=unique_name)

    def build_factory(self, build_type):
        return giit.factory.build_factory(build_type=build_type)

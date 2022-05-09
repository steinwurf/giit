#!/usr/bin/env python
# encoding: utf-8

import tempfile
import os
import fnmatch
import logging
import shutil

import giit.logs
import giit.giit_json
import giit.config


class Build(object):
    def __init__(
        self,
        step,
        repository,
        factory,
        build_path=None,
        giit_path=None,
        config_path=None,
        config_branch=None,
        task_filters=None,
        variables=[],
        verbose=False,
    ):

        self.step = step
        self.repository = repository
        self.factory = factory
        self.build_path = self._expand_path(path=build_path)
        self.giit_path = self._expand_path(path=giit_path)
        self.config_path = self._expand_path(path=config_path)
        self.config_branch = config_branch
        self.task_filters = task_filters
        self.extra_variables = variables
        self.verbose = verbose

    def _expand_path(self, path):
        if path:
            return os.path.abspath(os.path.expanduser(path))
        else:
            return path

    def run(self):

        # Setup giit data path
        if not self.giit_path:
            self.giit_path = os.path.join(tempfile.gettempdir(), "giit", "data")

        if not os.path.isdir(self.giit_path):
            os.makedirs(self.giit_path)

        # Setup logging
        giit.logs.setup_logging(giit_path=self.giit_path, verbose=self.verbose)

        # Create the build build log
        log = logging.getLogger("giit.main")

        # Add details to log file
        log.debug("build_path=%s", self.build_path)
        log.debug("giit_path=%s", self.giit_path)
        log.debug("config_branch=%s", self.config_branch)
        log.debug("config_path=%s", self.config_path)

        log.info("Lets go: %s", self.step)

        # Resolve the repository
        factory = self.factory.resolve_factory(
            giit_path=self.giit_path, repository=self.repository
        )

        git_repository = factory.build()

        # Set the build path
        if not self.build_path:
            self.build_path = os.path.join(
                self.giit_path, "build", git_repository.unique_name()
            )

        # If the step is clean we do it without fetching or cloning
        if self.step == "clean":

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
        json_config = giit.giit_json.GiitJson(
            git_repository=git_repository,
            log=logging.getLogger("giit.giit_json"),
            config_path=self.config_path,
            config_branch=self.config_branch,
        )

        config = json_config.read()

        if self.step not in config:
            raise RuntimeError(
                "Error step {} not found in {}".format(self.step, config)
            )

        # We will only use the configuration for the step
        config = config[self.step]

        # There can be several "sub-configurations" in a step, lets
        # make sure the config is a list. So we can handle the cases
        # uniformly
        if not isinstance(config, list):
            config = [config]

        # Get the tasks for all the substeps
        tasks = []

        for subconfig in config:
            tasks += self._generate_tasks(
                config=subconfig, git_repository=git_repository
            )

        if len(tasks) == 0:
            raise RuntimeError(
                "No tasks were generated. Check your filters, "
                "they did not match any of the available "
                "branches or tags."
            )

        log.info("Tasks generated %d", len(tasks))

        if self.task_filters is not None:
            log.info("Task filters: %s", ", ".join(self.task_filters))
            filtered_tasks = []
            for task in tasks:
                if any(
                    fnmatch.fnmatch(task.name(), filter) for filter in self.task_filters
                ):
                    filtered_tasks.append(task)
                else:
                    log.info("Skipped task: %s", task)
            tasks = filtered_tasks

        for idx, task in enumerate(tasks, 1):
            log.info("Running task [%d/%d]: %s", idx, len(tasks), task)
            task.run()

    def _generate_tasks(self, config, git_repository):

        log = logging.getLogger("giit.main")

        build_factory = self.factory.build_factory()

        # Validate the configuration
        config = giit.config.validate_config(config=config)

        for key, value in self.extra_variables:
            if key not in config["variables"]:
                log.debug("Adding extra variable '%s': %s", key, value)
                config["variables"][key] = value

        # Provide the different needed by the factory
        build_factory.provide_value(name="config", value=config)
        build_factory.provide_value(name="build_path", value=self.build_path)
        build_factory.provide_value(name="giit_path", value=self.giit_path)
        build_factory.provide_value(name="git_repository", value=git_repository)

        task_generator = build_factory.build()
        tasks = task_generator.tasks()

        return tasks

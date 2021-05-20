#!/usr/bin/env python
# encoding: utf-8

import os
import json


class GiitJson(object):
    def __init__(self, git_repository, log, config_path=None, config_branch=None):

        self.git_repository = git_repository
        self.log = log
        self.config_path = config_path
        self.config_branch = config_branch

    def read(self):

        if [self.config_path, self.config_branch].count(None) == 0:
            raise RuntimeError(
                "You can only specify either the "
                "--config_path or --config_branch option, not both."
            )

        if self.config_path:
            return self._from_path()

        if self.config_branch:
            return self._from_branch()

        if self.git_repository.workingtree_path():
            return self._from_workingtree()
        else:
            return self._from_default_branch()

    def _from_path(self):
        self.log.info("Using giit.json from path %s", self.config_path)

        with open(self.config_path, "r") as config_file:
            return json.load(config_file)

    def _from_branch(self):
        self.log.info("Using giit.json from branch %s", self.config_branch)

        self.git_repository.checkout_branch(remote_branch=self.config_branch)

        config_path = os.path.join(self.git_repository.repository_path(), "giit.json")

        with open(config_path, "r") as config_file:
            return json.load(config_file)

    def _from_workingtree(self):

        config_path = os.path.join(self.git_repository.workingtree_path(), "giit.json")

        self.log.info("Using giit.json from workingtree %s", config_path)

        with open(config_path, "r") as config_file:
            return json.load(config_file)

    def _from_default_branch(self):
        default_branch = self.git_repository.default_branch()
        self.log.info(f"Using giit.json from default branch origin/{default_branch}")
        self.git_repository.checkout_branch(remote_branch=f"origin/{default_branch}")

        config_path = os.path.join(self.git_repository.repository_path(), "giit.json")

        with open(config_path, "r") as config_file:
            return json.load(config_file)

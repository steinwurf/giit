#! /usr/bin/env python
# encoding: utf-8

import os
import sys
import hashlib
import tempfile
import shutil

import giit.config_reader
import giit.copy_directory


class PushCommand(object):

    def __init__(self, prompt, config, log):
        """
        :param config: A PushConfig object
        :param log: The log to use
        """
        self.prompt = prompt
        self.config = config
        self.log = log

    def run(self, context):
        """ Run the git push command based on the context

        :param context: A dict containing the context of the command
        """

        self.log.debug("context=%s", context)

        reader = giit.config_reader.ConfigReader(
            config=self.config, context=context)

        # We allow / to be the root of the remote branch, but
        # we need to handle that a bit carefully. Since the

        temp_path = os.path.join(tempfile.gettempdir(), 'giit_push')

        if os.path.isdir(temp_path):
            shutil.rmtree(temp_path, ignore_errors=True)

        directory = giit.copy_directory.CopyDirectory()

        from_path = reader.from_path
        to_path = self._to_path(
            repository_path=temp_path, to_path=reader.to_path)

        exclude_patterns = reader.exclude_patterns

        directory.copy(from_path=from_path,
                       to_path=to_path,
                       exclude_patterns=exclude_patterns)

        if reader.nojekyll:
            nojekyll_path = os.path.join(temp_path, '.nojekyll')
            open(nojekyll_path, 'a').close()

        command = ["git", "init"]
        self.prompt.run(command=command, cwd=temp_path)

        command = ["git", "add", "."]
        self.prompt.run(command=command, cwd=temp_path)

        commit_name = reader.commit_name
        commit_email = reader.commit_email

        command = ["git", "-c", "user.name='{}'".format(commit_name),
                   "-c", "user.email='{}'".format(commit_email),
                   "commit", "-m", "'giit push'"]
        self.prompt.run(command=command, cwd=temp_path)

        git_url = reader.git_url
        target_branch = reader.target_branch

        self.log.info("Pushing %s to branch %s", from_path,
                      target_branch)

        command = [
            'git', 'push', '--force',
            "{}".format(git_url),
            'master:{}'.format(target_branch)
        ]

        self.prompt.run(command=command, cwd=temp_path)

    @staticmethod
    def _to_path(repository_path, to_path):

        if os.path.isabs(to_path):
            # Make path relative
            to_path = '.' + to_path

        path = os.path.join(repository_path, to_path)
        path = os.path.normpath(path)

        return path

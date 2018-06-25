#! /usr/bin/env python
# encoding: utf-8

import os
import sys
import hashlib
import shutil
import logging

import giit.prompt


URL = 'https://github.com/pypa/virtualenv.git'
VERSION = '15.1.0'


class VirtualEnv(object):
    """ Simple object which can be used to work within a virtualenv.


    venv = VirtualEnv.create(cwd='/tmp', runner=command.run, name=None)

    It is important to be aware of the cwd parameter, e.g. if you access files
    etc. it will be relative to cwd. So if cwd is the 'build' directory and you
    access a file in the root of the repository it will need to be prefixed
    with '../somefile.txt'.
    """

    def __init__(self, prompt, log):

        self.prompt = prompt
        self.log = log

    def create_environment(self, path):

        if not os.path.isdir(path):

            args = ['python', '-m', 'virtualenv', path,
                    '--no-site-packages']

            self.prompt.run(command=args)

        # Create a new environment based on the new virtualenv
        env = dict(os.environ)

        # Make sure the virtualenv Python executable is first in PATH
        if sys.platform == 'win32':
            python_path = os.path.join(path, 'Scripts')
        else:
            python_path = os.path.join(path, 'bin')

        env['PATH'] = os.path.pathsep.join([python_path, env['PATH']])

        return env

    @staticmethod
    def from_git(git, clone_path, log):

        if not os.path.isdir(clone_path):
            os.makedirs(clone_path)

        repo_path = os.path.join(clone_path, VERSION)

        if not os.path.isdir(repo_path):

            log.debug('Cloning {} into {}'.format(URL, repo_path))

            git.clone(repository=URL, directory=repo_path,
                      cwd=clone_path)

            git.checkout(branch=VERSION, cwd=repo_path)

        log.debug('Using virtualenv from {}'.format(repo_path))

        env = dict(os.environ)
        env.update({'PYTHONPATH': repo_path})

        p = giit.prompt.Prompt(env=env)

        return VirtualEnv(prompt=p, log=log)


class NameToPathAdapter(object):

    def __init__(self, virtualenv, virtualenv_root_path):
        self.virtualenv = virtualenv
        self.virtualenv_root_path = virtualenv_root_path

    def create_environment(self, name):

        path = os.path.join(self.virtualenv_root_path, name)

        return self.virtualenv.create_environment(path=path)

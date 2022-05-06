#!/usr/bin/env python
# encoding: utf-8

import os
import logging
import copy

import giit.prompt
import giit.git
import giit.git_url_parser
import giit.git_repository
import giit.cache
import giit.venv
import giit.tasks
import giit.config
import giit.python_environment
import giit.python_command
import giit.push_config
import giit.push_command


class Factory(object):
    def __init__(self):

        self.default_build = None
        self.providers = {}

    def set_default_build(self, default_build):
        self.default_build = default_build

    def provide_value(self, name, value, override=False):

        if override:
            assert name in self.providers
        else:
            assert name not in self.providers

        def call():
            return value

        self.providers[name] = call

    def provide_function(self, name, function, override=False):

        if override:
            assert name in self.providers
        else:
            assert name not in self.providers

        def call():
            return function(self)

        self.providers[name] = call

    def require(self, name):
        return self.providers[name]()

    def build(self):
        return self.require(name=self.default_build)


def require_prompt(factory):
    return giit.prompt.Prompt()


def require_git(factory):

    prompt = factory.require(name="prompt")
    git_binary = factory.require(name="git_binary")
    log = logging.getLogger(name="giit.git")

    return giit.git.Git(git_binary=git_binary, prompt=prompt, log=log)


def require_git_url_parser(factory):
    return giit.git_url_parser.GitUrlParser()


def require_virtualenv(factory):
    virtualenv_root_path = factory.require(name="virtualenv_root_path")
    log = logging.getLogger(name="giit.virtualenv")
    prompt = factory.require(name="prompt")
    venv = giit.venv.VirtualEnv(prompt=prompt, log=log)

    venv = giit.venv.NameToPathAdapter(
        virtualenv=venv, virtualenv_root_path=virtualenv_root_path
    )

    return venv


def require_git_repository(factory):
    git = factory.require(name="git")
    git_url_parser = factory.require(name="git_url_parser")
    repository = factory.require(name="repository")
    log = logging.getLogger(name="giit.git_repository")
    clone_path = factory.require(name="clone_path")

    return giit.git_repository.GitRepository(
        git=git,
        git_url_parser=git_url_parser,
        clone_path=clone_path,
        log=log,
        repository=repository,
    )  # , remote_branch=remote_branch)


def provide_output_path(factory):

    return factory.require(name="giit_path")


def provide_clone_path(factory):

    giit_path = factory.require(name="giit_path")

    return os.path.join(giit_path, "clones")


def provide_virtualenv_root_path(factory):

    giit_path = factory.require(name="giit_path")

    return os.path.join(giit_path, "virtualenvs")


def require_cache(factory):

    giit_path = factory.require(name="giit_path")
    unique_name = factory.require(name="unique_name")

    return giit.cache.Cache(cache_path=giit_path, unique_name=unique_name)


def require_branch_generator(factory):

    git_repository = factory.require(name="git_repository")
    command = factory.require(name="command")
    config = factory.require(name="config")
    build_path = factory.require(name="build_path")

    return giit.tasks.GitBranchGenerator(
        git_repository=git_repository,
        command=command,
        config=copy.deepcopy(config),
        build_path=build_path,
    )


def require_tag_generator(factory):

    git_repository = factory.require(name="git_repository")
    command = factory.require(name="command")
    config = factory.require(name="config")
    build_path = factory.require(name="build_path")

    return giit.tasks.GitTagGenerator(
        git_repository=git_repository,
        command=command,
        config=copy.deepcopy(config),
        build_path=build_path,
    )


def require_workingtree_generator(factory):

    git_repository = factory.require(name="git_repository")
    command = factory.require(name="command")
    config = factory.require(name="config")
    build_path = factory.require(name="build_path")

    return giit.tasks.WorkingtreeGenerator(
        git_repository=git_repository,
        command=command,
        config=copy.deepcopy(config),
        build_path=build_path,
    )


def require_no_git_generator(factory):

    command = factory.require(name="command")
    config = factory.require(name="config")
    build_path = factory.require(name="build_path")

    return giit.tasks.NoGitGenerator(
        command=command, config=copy.deepcopy(config), build_path=build_path
    )


def require_task_generator(factory):

    task_generator = giit.tasks.TaskFactory()

    config = factory.require(name="config")

    if config["no_git"]:
        no_git = factory.require(name="no_git_generator")
        task_generator.add_generator(no_git)

    else:
        workingtree_generator = factory.require(name="workingtree_generator")
        task_generator.add_generator(workingtree_generator)

        branch_generator = factory.require(name="branch_generator")
        task_generator.add_generator(branch_generator)

        tag_generator = factory.require(name="tag_generator")
        task_generator.add_generator(tag_generator)

    return task_generator


def resolve_factory(giit_path, repository):

    factory = Factory()
    factory.set_default_build(default_build="git_repository")

    factory.provide_value(name="git_binary", value="git")
    factory.provide_value(name="giit_path", value=giit_path)
    factory.provide_value(name="repository", value=repository)
    # factory.provide_value(name='remote_branch', value=remote_branch)

    factory.provide_function(name="clone_path", function=provide_clone_path)
    factory.provide_function(name="git_url_parser", function=require_git_url_parser)
    factory.provide_function(name="git", function=require_git)
    factory.provide_function(name="git_repository", function=require_git_repository)
    factory.provide_function(name="prompt", function=require_prompt)

    return factory


def cache_factory(giit_path, unique_name):

    factory = Factory()
    factory.set_default_build(default_build="cache")
    factory.provide_value(name="giit_path", value=giit_path)
    factory.provide_value(name="unique_name", value=unique_name)
    factory.provide_function(name="cache", function=require_cache)

    return factory


def require_python_environment(factory):

    prompt = factory.require(name="prompt")
    virtualenv = factory.require(name="virtualenv")
    log = logging.getLogger(name="giit.python_environment")

    return giit.python_environment.PythonEnvironment(
        prompt=prompt, virtualenv=virtualenv, log=log
    )


def require_command(factory):

    # config = factory.require(name='config')
    environment = factory.require(name="python_environment")
    prompt = factory.require(name="prompt")
    log = logging.getLogger(name="giit.python_command")

    return giit.python_command.PythonCommand(
        environment=environment, prompt=prompt, log=log
    )


def build_factory():

    factory = Factory()
    factory.set_default_build(default_build="require_task_generator")

    factory.provide_function(name="prompt", function=require_prompt)

    factory.provide_function(
        name="python_environment", function=require_python_environment
    )

    factory.provide_function(name="command", function=require_command)

    factory.provide_function(name="output_path", function=provide_output_path)
    factory.provide_function(name="clone_path", function=provide_clone_path)

    factory.provide_function(
        name="virtualenv_root_path", function=provide_virtualenv_root_path
    )

    factory.provide_value(name="git_binary", value="git")

    factory.provide_function(name="git_url_parser", function=require_git_url_parser)
    factory.provide_function(name="git", function=require_git)

    factory.provide_function(name="virtualenv", function=require_virtualenv)

    factory.provide_function(
        name="require_task_generator", function=require_task_generator
    )

    factory.provide_function(name="branch_generator", function=require_branch_generator)

    factory.provide_function(name="tag_generator", function=require_tag_generator)

    factory.provide_function(
        name="workingtree_generator", function=require_workingtree_generator
    )

    factory.provide_function(name="no_git_generator", function=require_no_git_generator)

    return factory

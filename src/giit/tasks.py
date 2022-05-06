#!/usr/bin/env python
# encoding: utf-8

import re
import semantic_version
import giit.config


class NoGitTask(object):
    def __init__(self, context, config, command):
        self.context = context
        self.config = config
        self.command = command

    def name(self):
        return self.context["name"]

    def run(self):

        task_config = giit.config.fill_dict(context=self.context, config=self.config)

        self.command.run(config=task_config)

    def __str__(self):
        return "scope '{scope}'".format(**self.context)


class NoGitGenerator(object):
    def __init__(self, command, config, build_path):
        """Create no_git task generator

        :param command: The command to run e.g. giit.python_command.PythonCommand
        :param config: The config e.g. giit.config.PythonConfig
        :param build_path: The build path as a string
        """

        self.command = command
        self.config = config
        self.build_path = build_path

    def tasks(self):

        if self.config["no_git"] == False:
            return []

        context = {
            "scope": "no_git",
            "name": "no_git",
            "build_path": self.build_path,
        }

        task = NoGitTask(config=self.config, context=context, command=self.command)

        return [task]


class WorkingtreeGenerator(object):
    def __init__(self, git_repository, command, config, build_path):
        """Create a tag generator.

        :param git_repository: A giit.git_repository.GitRepository instance
        :param command: The command to run e.g.giit.python_command.PythonCommand
        :param config: The config e.g. giit.config.PythonConfig
        :param build_path: The build path as a string
        """

        self.git_repository = git_repository
        self.command = command
        self.config = config
        self.build_path = build_path

    def tasks(self):

        if self.config["workingtree"] == False:
            return []

        if self.git_repository.workingtree_path():

            context = {
                "scope": "workingtree",
                "name": "workingtree",
                "checkout": "workingtree",
                "build_path": self.build_path,
                "source_path": self.git_repository.workingtree_path(),
            }

            task = NoGitTask(config=self.config, context=context, command=self.command)

            return [task]

        else:

            return []


class GitTask(object):
    def __init__(self, git_repository, config, context, command):
        self.git_repository = git_repository
        self.config = config
        self.context = context
        self.command = command

    def run(self):

        checkout = self.context["checkout"]
        scope = self.context["scope"]

        if scope == "branch":
            self.git_repository.checkout_branch(remote_branch=checkout)

        elif scope == "tag":
            self.git_repository.checkout_tag(tag=checkout)

        else:
            raise RuntimeError("Unknown scope {}".format(scope))

        task_config = giit.config.fill_dict(context=self.context, config=self.config)

        self.command.run(config=task_config)

    def name(self):
        return self.context["name"]

    def __str__(self):
        return "scope '{scope}' name '{name}' checkout '{checkout}'".format(
            **self.context
        )


class GitBranchGenerator(object):
    def __init__(self, git_repository, command, config, build_path):
        """Create a branch generator.

        :param git_repository: A giit.git_repository.GitRepository instance
        :param repository_path: Path to where the repository is.
        :param command: The command to run e.g.
            giit.python_command.PythonCommand
        :param build_path: The build path as a string
        :param branches: The list of branches to build
        :param log: A logging object
        """

        self.git_repository = git_repository
        self.command = command
        self.config = config
        self.build_path = build_path

    def tasks(self):

        tasks = []

        for branch in self.git_repository.remote_branches():

            if not self._match_branch(branch=branch):
                continue

            # Create the human readable name for the branch. The "name"
            # is available in the different steps. It is typically used
            # to control where in the build directory the output of
            # a command should go.
            if branch.startswith("origin/"):
                name = re.sub("^origin/", "", branch)
            else:
                name = branch

            # Replace / in branch names
            name = name.replace("/", "_")

            context = {
                "scope": "branch",
                "name": name,
                "checkout": branch,
                "build_path": self.build_path,
                "source_path": self.git_repository.repository_path(),
            }

            task = GitTask(
                git_repository=self.git_repository,
                context=context,
                config=self.config,
                command=self.command,
            )

            tasks.append(task)

        return tasks

    def _match_branch(self, branch):
        """Checks the branch name against the filters.

        :return: True if the branch matches the filter otherwise False
        """

        regex_filters = self.config["branches"]["regex"]["filters"]

        for regex_filter in regex_filters:

            if re.match(regex_filter, branch):
                return True

        if not self.config["branches"]["source_branch"]:
            return False

        source_branch = self.git_repository.source_branch()

        if source_branch == branch:
            return True

        return False


class GitTagGenerator(object):
    def __init__(self, git_repository, command, config, build_path):
        """Create a tag generator.

        :param git_repository: A giit.git_repository.GitRepository instance
        :param command: The command to run e.g.giit.python_command.PythonCommand
        :param config: The config e.g. giit.config.PythonConfig
        :param build_path: The build path as a string
        """

        self.git_repository = git_repository
        self.command = command
        self.config = config
        self.build_path = build_path

    def tasks(self):

        tasks = []

        tags = self.git_repository.tags()

        for tag in reversed(tags):

            if not self._match_tag(tag=tag):
                continue

            context = {
                "scope": "tag",
                "name": tag,
                "checkout": tag,
                "build_path": self.build_path,
                "source_path": self.git_repository.repository_path(),
            }

            task = GitTask(
                git_repository=self.git_repository,
                context=context,
                config=self.config,
                command=self.command,
            )

            tasks.append(task)

        return tasks

    def _match_tag(self, tag):
        """Checks the tag name against the filters.

        :return: True if the tag matches the filter otherwise False
        """

        regex_filters = self.config["tags"]["regex"]["filters"]

        for regex_filter in regex_filters:

            if re.match(regex_filter, tag):
                return True

        semver_filters = self.config["tags"]["semver"]["filters"]
        semver_relaxed = self.config["tags"]["semver"]["relaxed"]

        for semver_filter in semver_filters:

            spec = semantic_version.Spec(semver_filter)
            if semver_relaxed:
                version = semantic_version.Version.coerce(tag)
            else:
                version = semantic_version.Version(tag)

            if spec.match(version):
                return True

        return False


class TaskFactory(object):
    def __init__(
        self,
    ):
        self.generators = []

    def add_generator(self, generator):
        self.generators.append(generator)

    def tasks(self):

        tasks = []

        for generator in self.generators:

            generator_tasks = generator.tasks()

            tasks += generator_tasks

        return tasks

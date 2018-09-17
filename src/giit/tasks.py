import json
import os
import shutil
import hashlib
import sys
import re
import semantic_version


class WorkingtreeTask(object):

    def __init__(self, context, command):
        self.context = context
        self.command = command

    def run(self):
        self.command.run(context=self.context)


class WorkingtreeGenerator(object):

    def __init__(self, git_repository, command, build_path):
        self.git_repository = git_repository
        self.command = command
        self.build_path = build_path

    def tasks(self):

        if self.git_repository.workingtree_path:

            context = {
                'scope': 'workingtree',
                'name': 'workingtree',
                'checkout': 'workingtree',
                'build_path': self.build_path,
                'source_path': self.git_repository.workingtree_path
            }

            task = WorkingtreeTask(context=context, command=self.command)

            return [task]

        else:

            return []


class GitTask(object):

    def __init__(self, git_repository, context, command):
        self.git_repository = git_repository
        self.context = context
        self.command = command

    def run(self):

        checkout = self.context['checkout']
        scope = self.context['scope']

        if scope == 'branch':
            self.git_repository.checkout_branch(
                remote_branche=checkout)

        elif scope == 'tag':
            self.git_repository.checkout_tag(
                tag=checkout)

        else:
            raise RuntimeError("Unknown scope {}".format(scope))

        self.command.run(context=self.context)

        # output_path = os.path.join(
        #     self.output_path, self.checkout_type, self.checkout)

        # sha1 = self.git.current_commit(cwd=cwd)

        # build_info.output_path = output_path
        # build_info.repository_path = self.repository_path
        # build_info.slug = self.checkout
        # build_info.type = self.checkout_type

        # if self.cache.match(sha1=sha1):
        #     path = self.cache.path(sha1=sha1)

        #     if path != output_path:
        #         shutil.copytree(src=path, dst=output_path)

        # else:

        #     self.sphinx.build(build_info=build_info)

        #     self.cache.update(sha1=sha1, path=output_path)


class GitBranchGenerator(object):

    def __init__(self, git_repository, command, config, build_path):
        """ Create a branch generator.

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
            if branch.startswith('origin/'):
                name = re.sub("^origin/", "", branch)
            else:
                name = branch

            # Replace / in branch names
            name = name.replace("/", "_")

            context = {
                'scope': 'branch',
                'name': name,
                'checkout': branch,
                'build_path': self.build_path,
                'source_path': self.git_repository.repository_path()
            }

            task = GitTask(git_repository=self.git_repository,
                           context=context,
                           command=self.command)

            tasks.append(task)

        return tasks

    def _match_branch(self, branch):
        """ Checks the branch name against the filters.

        :return: True if the branch matches the filter otherwise False
        """

        regex_filters = self.config.branches["regex_filters"]

        for regex_filter in regex_filters:

            if re.match(regex_filter, branch):
                return True

        return False


class GitTagGenerator(object):

    def __init__(self, git, git_repository, command, build_path,
                 tag_semver_filter):

        self.git = git
        self.git_repository = git_repository
        self.command = command
        self.build_path = build_path
        self.tag_semver_filter = tag_semver_filter

    def tasks(self):

        tasks = []

        tags = self.git_repository.tags()

        if self.tag_semver_filter:

            spec = semantic_version.Spec(self.tag_semver_filter)
            versions = [semantic_version.Version(t) for t in tags]
            tags = [str(tag) for tag in spec.filter(versions)]

        for tag in tags:

            context = {
                'scope': 'tag',
                'name': tag,
                'checkout': tag,
                'build_path': self.build_path,
                'source_path': self.git_repository.giit_clone_path
            }

            task = GitTask(git=self.git, context=context,
                           command=self.command)

            tasks.append(task)

        return tasks


class TaskFactory(object):

    def __init__(self, ):
        self.generators = []

    def add_generator(self, generator):
        self.generators.append(generator)

    def tasks(self):

        tasks = []

        for generator in self.generators:

            generator_tasks = generator.tasks()

            tasks += generator_tasks

        return tasks

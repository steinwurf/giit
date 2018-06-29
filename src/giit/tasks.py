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

    def __init__(self, git, context, command):
        self.git = git
        self.context = context
        self.command = command

    def run(self):

        cwd = self.context['source_path']
        checkout = self.context['checkout']

        # The git reset fails if the branch is only on the remote
        # so we first do a checkout
        #self.git.checkout(branch=checkout, force=True, cwd=cwd)

        # https://stackoverflow.com/a/8888015/1717320
        self.git.reset(branch=checkout, hard=True, cwd=cwd)

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

    def __init__(self, git, repository_path, command, build_path,
                 remote_branch, branches):
        """ Create a branch generator.

        :param git: A giit.git.Git instance
        :param repository_path: Path to where the repository is.
        :param command: The command to run e.g.
            giit.python_command.PythonCommand
        :param build_path: The build path as a string
        :param remote_branch: The source branch as a string
        :param branches: The list of branches to build
        """

        self.git = git
        self.remote_branch = remote_branch
        self.repository_path = repository_path
        self.command = command
        self.build_path = build_path
        self.branches = branches

    def tasks(self):

        # Create a task for the source branch if it is not already
        # included in the branches list
        if self.remote_branch not in self.branches:
            self.branches.append(self.remote_branch)

        tasks = []

        for branch in self.branches:

            # We omit origin if in the branch name. For others
            # we will include the remote name.
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
                'source_path': self.repository_path
            }

            task = GitTask(git=self.git, context=context,
                           command=self.command)

            tasks.append(task)

        return tasks


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
                'source_path': self.git_repository.repository_path
            }

            task = GitTask(git=self.git, context=context,
                           command=self.command)

            tasks.append(task)

        return tasks


class TaskFactory(object):

    def __init__(self):
        self.generators = []

    def add_generator(self, generator):
        self.generators.append(generator)

    def tasks(self):

        tasks = []

        for generator in self.generators:

            generator_tasks = generator.tasks()

            tasks += generator_tasks

        return tasks

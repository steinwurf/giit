#!/usr/bin/env python
# encoding: utf-8

import os
import re


class Git(object):
    def __init__(self, git_binary, prompt, log):
        """Construct a new Git instance.

        :param git_binary: A string containing the path to a git executable.
        :param ctx: A Waf Context instance.
        """
        self.git_binary = git_binary
        self.prompt = prompt
        self.log = log

    def version(self):
        """
        Runs 'git version' and return the version information as a tuple

        Example:

            If the output looks like "git version 1.8.1.msysgit.1"
            we just extract the integers i.e. (1.8.1.1)
        """
        args = [self.git_binary, "version"]
        result = self.prompt.run(args)

        int_list = [int(s) for s in re.findall("\\d+", result.stdout)]
        return tuple(int_list)

    def current_commit(self, cwd, ref="HEAD"):
        """
        Runs 'git rev-parse HEAD' parse and return the commit id (SHA1) of the
        commit currently checked out into the working copy.
        """
        args = [self.git_binary, "rev-parse", ref]
        result = self.prompt.run(args, cwd=cwd)

        return result.stdout.strip()

    def clone(self, repository, directory, cwd):
        """
        Runs 'git clone <repository> <directory>' in the directory cwd.
        """
        args = [self.git_binary, "clone", repository, directory]
        self.prompt.run(args, cwd=cwd)

    def pull(self, cwd):
        """
        Runs 'git pull' in the directory cwd
        """

        args = [self.git_binary, "pull"]
        self.prompt.run(args, cwd=cwd)

    def fetch(self, repository, all, prune, cwd):
        """
        Runs 'git fetch' in the directory cwd
        """

        args = [self.git_binary, "fetch", repository]

        if all:
            args.append("--all")

        if prune:
            args.append("--prune")

        self.prompt.run(args, cwd=cwd)

    def default_branch(self, cwd):
        """
        Returns the default branch, this is usually master or main.
        """
        args = [self.git_binary, "symbolic-ref", "--short HEAD"]

        result = self.prompt.run(args, cwd=cwd)

        self.log.debug("default_branch=%s", result)
        return result

    def current_branch(self, cwd):
        """
        Uses git.branch(...) but only returns the current one
        """
        current, _ = self._branch(cwd=cwd)

        return current

    def local_branches(self, cwd):
        current, others = self._branch(cwd=cwd)

        return others.append(current)

    def remote_branches(self, cwd):
        _, remote = self._branch(cwd=cwd, remote=True)
        return remote

    def _branch(self, cwd, remote=False):
        """
        Runs 'git branch' and returns the current branch and a list of
        additional branches
        """
        args = [self.git_binary, "branch"]

        if remote:
            args.append("-r")

        result = self.prompt.run(args, cwd=cwd)

        self.log.debug("branch remote=%s %s", remote, result)

        if remote:
            return self._parse_branch_remote(result=result)
        else:
            return self._parse_branch_local(result=result)

    def _parse_branch_remote(self, result):

        branch = result.stdout.split("\n")
        branch = [b.strip() for b in branch if b != ""]

        parsed = []

        for b in branch:
            if "origin/HEAD ->" in b:
                continue

            parsed.append(b.strip())

        return None, parsed

    def _parse_branch_local(self, result):

        branch = result.stdout.split("\n")
        branch = [b.strip() for b in branch if b != ""]

        current = ""
        others = []

        for b in branch:
            if b.startswith("*"):
                current = b[1:].strip()
            else:
                others.append(b)

        if current == "":
            raise RuntimeError("Failed to locate current branch")

        return current, others

    def reset(self, hard, branch, cwd):
        args = [self.git_binary, "reset"]

        if hard:
            args.append("--hard")

        args.append(branch)
        args.append("--")

        self.prompt.run(args, cwd=cwd)

    def is_detached_head(self, cwd):
        """
        Checks if the repository is in detached HEAD state. See learn what this
        means read here:

            https://git-scm.com/docs/git-checkout
        """
        current, _ = self.branch(cwd=cwd)

        # Different git versions denote the detached HEAD state differently,
        # possible variants are the following:
        # * (no branch)
        # * (detached from waf-1.9.7)
        # * (HEAD detached at waf-1.9.7)
        return current.startswith("(") and current.endswith(")")

    def checkout(self, branch, cwd, force=False, worktree=None, orphan=False):
        """
        Runs 'git checkout branch'
        """

        args = [self.git_binary]

        if worktree:
            args.append("--work-tree")
            args.append(worktree)

        args.append("checkout")

        if orphan:
            args.append("--orphan")

        if force:
            args.append("--force")

        args.append(branch)

        self.prompt.run(args, cwd=cwd)

    def has_submodules(run, cwd):
        """
        Returns true if the repository in directory cwd contains the
        .gitmodules file.
        """
        return os.path.isfile(os.path.join(cwd, ".gitmodules"))

    def sync_submodules(self, cwd):
        """
        Runs 'git submodule sync' in the directory cwd
        """
        args = [self.git_binary, "submodule", "sync"]
        self.prompt.run(args, cwd=cwd)

    def init_submodules(self, cwd):
        """
        Runs 'git submodule init' in the directory cwd
        """
        args = [self.git_binary, "submodule", "init"]
        self.prompt.run(args, cwd=cwd)

    def update_submodules(self, cwd):
        """
        Runs 'git submodule update' in the directory cwd
        """
        args = [self.git_binary, "submodule", "update"]
        self.prompt.run(args, cwd=cwd)

    def pull_submodules(self, cwd):
        """
        Runs 'git submodule sync', 'git submodule init', and
        'git submodule update' unless the repository doesn't have submodules.
        """
        if self.has_submodules(cwd=cwd):
            self.sync_submodules(cwd=cwd)
            self.init_submodules(cwd=cwd)
            self.update_submodules(cwd=cwd)

    def tags(self, cwd):
        """
        Runs 'git tag -l' in the directory cwd and returns the tags

        :param cwd: The current working directory as a string
        """
        args = [self.git_binary, "tag", "-l"]
        result = self.prompt.run(args, cwd=cwd)

        tags = result.stdout.split("\n")
        return [t for t in tags if t != ""]

    def remote_origin_url(self, cwd):
        """
        Runs 'git config --get remote.origin.url' in the directory cwd and
        returns the value

        :param cwd: The current working directory as a string
        """
        args = [self.git_binary, "config", "--get", "remote.origin.url"]
        result = self.prompt.run(args, cwd=cwd)

        url = result.stdout.strip()

        if os.path.isdir(url):
            # The remote may be a local directory - that has
            # an actual remote url
            return self.remote_origin_url(cwd=url)
        else:
            return url

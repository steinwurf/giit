import os
import hashlib
import json


class GitRepository(object):

    def __init__(self, repository, git, git_url_parser, clone_path, log):
        """ Create a new instance.

        :param repository: The repository either as an URL or path to a
            local repository
        :param git: The Git object used to run git commands.
        :param git_url_parser: Parser to extract information from
            the git URL
        :param clone_path: The user specified where clones should
            be made
        :param log: A logging object
        """
        self.repository = repository
        self.git = git
        self.git_url_parser = git_url_parser
        self.clone_path = os.path.abspath(os.path.expanduser(clone_path))
        self.log = log

    def workingtree_path(self):
        """ :return: The path to the workingtree if there is not workingtree
                     return None
        """
        if os.path.isdir(self.repository):
            return os.path.abspath(os.path.expanduser(self.repository))
        else:
            return None

    def git_url(self):
        """ :return: The Git repository URL """
        if os.path.isdir(self.repository):
            return self.git.remote_origin_url(cwd=self.repository)
        else:
            return self.repository

    def unique_name(self):
        """ :return: A unique name for this repository """
        # Compute the clone path
        git_url = self.git_url()
        git_info = self.git_url_parser.parse(url=git_url)

        url_hash = hashlib.sha1(git_url.encode('utf-8')).hexdigest()[:6]
        return git_info.name + '-' + url_hash

    def repository_path(self):
        """ :return: The path where we clone the repository """
        return os.path.join(self.clone_path, self.unique_name())

    def source_branch(self):
        """ The source branch.

        When passing a path to giit the source branch will be the branch
        currently checked out for that path. When passing an URL to giit we
        return None
        """

        # If we were not passed an URL
        if not self.workingtree_path():
            return None

        # Check if the current branch has a corresponding remote i.e. if
        # it has been pushed.
        current = self.git.current_branch(cwd=self.workingtree_path)

        # Fetch a list of remote branches
        remote_branches = self.git.remote_branches(cwd=self.repository_path)

        # The remote branches are in a list of "remote/branch"
        match = []
        for remote_branch in remote_branches:
            remote, branch = remote_branch.split("/")

            if branch == current:
                match.append(remote_branch)

        matches = len(match)

        if matches == 0:
            self.log.debug(
                "Skipping source branch: No remote branch tracking %s. These "
                "remote branches were found in "
                "the repository: %s.\nYou probably just need to "
                "push the branch you are working on:\n\n"
                "\tgit push -u origin %s\n" % (current, remote_branches,
                                               current))

            return None

        if matches > 1:
            raise RuntimeError(
                "Several remote branches %s for %s" % (remote_branches, current))

        remote = match[0]
        self.log.debug('source branch %s' % remote)
        return remote

    def clone(self):
        """ Clones the repository.
        """

        if not os.path.isdir(self.clone_path):
            os.makedirs(self.clone_path)

        self.log.info("Using git version: %s",
                      ".".join([str(i) for i in self.git.version()]))

        # Get the URL to the repository
        git_url = self.git_url()
        self.log.info("Using git repository: %s", git_url)

        repository_path = self.repository_path()

        self.log.debug("repository_path=%s", repository_path)

        # Get the updates
        if os.path.isdir(repository_path):
            self.log.info('Running: git fetch in %s', repository_path)
            self.git.fetch(cwd=repository_path, all=True, prune=True)

        else:
            self.log.info('Running: git clone into %s', repository_path)
            self.git.clone(repository=git_url, directory=repository_path,
                           cwd=self.clone_path)

    def remote_branches(self):
        """ :return: The re,pte brances specified for the repository """
        assert os.path.isdir(self.repository_path())

        return self.git.remote_branches(cwd=self.repository_path())

    def tags(self):
        """ :return: The tags specified for the repository """
        assert os.path.isdir(self.repository_path())

        return self.git.tags(cwd=self.repository_path())

    def checkout_branch(self, remote_branch):
        """ Checkout a specific branch.

        The branch must be a remote-tracking branch.
        """

        # Check if the branch exists
        remotes = self.remote_branches()

        if remote_branch not in remotes:
            raise RuntimeError("No remote branch %s. These branches exits "
                               "in the repository %s" % (remote_branch, remotes))

        self._checkout(checkout=remote_branch)

    def checkout_tag(self, tag):
        """ Checkout a specific tag."""

        # Check if the tag exists
        tags = self.tags()

        if tag not in tags:
            raise RuntimeError("No tag %s. These tags exits "
                               "in the repository %s" % (tag, tags))

        self._checkout(checkout=tag)

    def _checkout(self, checkout):
        # https://stackoverflow.com/a/8888015/1717320
        self.git.reset(branch=checkout, hard=True, cwd=self.repository_path())

    # def load_json_config(self):

    #     if self.workingtree_path:
    #         json_config = os.path.join(self.workingtree_path, 'giit.json')

    #         self.log.info("Using giit.json from %s workingtree",
    #                       self.workingtree_path)

    #         with open(json_config, 'r') as config_file:
    #             return json.load(config_file)

    #     # We only support building branches remote branches. The reason for
    #     # this it that it makes it easier to know what is the state of a given
    #     # branch. Two users might be on the same branch but have different
    #     # changes. Since we only build the remote we force users to push their
    #     # changes and thereby we have one source of truth of what is on a given
    #     # branch. Namely what has been pushed to the remote. Lets get the
    #     # corresponding remote branch

    #     # Make sure we start on the source branch, we may
    #     # read the giit.json file from here
    #     self.git.checkout(branch=self.giit_branch, cwd=self.giit_clone_path)

    #     json_config = os.path.join(self.giit_clone_path, 'giit.json')

    #     self.log.info("Using giit.json from %s branch", self.giit_branch)

    #     with open(json_config, 'r') as config_file:
    #         return json.load(config_file)

import os
import hashlib
import json


class GitRepository(object):

    def __init__(self, repository, git, git_url_parser, clone_path, log):
                 # source_branch, log):
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

    @property
    def workingtree_path(self):
        """ :return: The path to the workingtree if there is not workingtree
                     return None
        """
        if os.path.isdir(self.repository):
            return os.path.abspath(os.path.expanduser(self.repository))
        else:
            return None

    @property
    def git_url(self):
        """ :return: The Git repository URL """
        if os.path.isdir(self.repository):
            return self.git.remote_origin_url(cwd=self.repository)
        else:
            return self.repository

    @property
    def unique_name(self):
        """ :return: A unique name for this repository """
        # Compute the clone path
        git_info = self.git_url_parser.parse(url=self.git_url)

        url_hash = hashlib.sha1(self.git_url.encode('utf-8')).hexdigest()[:6]
        return git_info.name + '-' + url_hash

    @property
    def giit_clone_path(self):
        """ :return: The path where we clone the repository """
        return os.path.join(self.clone_path, self.unique_name)

    @property
    def source_branch(self):
        """ :return: The source branch. When passing a path to giit the
                     source branch will be the branch currently checked out
                     for that path. When passing an URL to giit we return None
        """

        if not self.workingtree_path:
            return None

        current = self.git.current_branch(cwd=self.workingtree_path)

        remotes = self.git.remote_branches(cwd=self.giit_clone_path)

        match = [remote for remote in remotes if current in remote]
        matches = len(match)

        if matches == 0:
            self.log.info(
                "Skipping build: No remote branch tracking %s. These remote "
                "branches were found in "
                "the repository: %s.\nYou probably just need to "
                "push the branch you are working on:\n\n"
                "\tgit push -u origin %s\n" % (current, remotes, current))

            return None

        if matches > 1:
            raise RuntimeError(
                "Several remote branches %s for %s" % (remotes, current))

        remote = match[0]
        self.log.debug('branch %s -> %s', current, remote)
        return remote

    def clone(self):
        """ Clones the repository.
        """

        if not os.path.isdir(self.clone_path):
            os.makedirs(self.clone_path)

        self.log.info("Using git version: %s",
                      ".".join([str(i) for i in self.git.version()]))

        # Get the URL to the repository
        self.log.info("Using git repository: %s", self.git_url)

        # Get the updates
        if os.path.isdir(self.giit_clone_path):
            self.log.info('Running: git fetch in %s', self.giit_clone_path)
            self.git.fetch(cwd=self.giit_clone_path, all=True, prune=True)
        else:
            self.log.info('Running: git clone into %s', self.giit_clone_path)
            self.git.clone(repository=self.git_url,
                           directory=self.giit_clone_path,
                           cwd=self.clone_path)

    def checkout(self, checkout):
        """ Ensures that the repository is on a specific checkout.

        The checkout can be a branch name, commit or tag.
        """

        # Check if this is a branch
        remotes = self.git.remote_branches(cwd=self.giit_clone_path)

        match = [remote for remote in remotes if current in remote]
        matches = len(match)

        if matches == 0:
            self.log.debub(
                "No remote branch tracking %s. These remote "
                "branches were found in "
                "the repository: %s." % (current, remotes))

        if matches > 1:
            raise RuntimeError(
                "Several remote branches %s for %s" % (remotes, current))

        remote = match[0]
        self.log.debug('branch %s -> %s', current, remote)
        return remote

    def checkout_branch(self, checkout):
        """ Checkout a specific branch.

        The branch must be a remote-tracking branch, but passing both
        master or origin/master should work.
        """

        # Check if this is a branch
        remotes = self.git.remote_branches(cwd=self.giit_clone_path)

        match = [remote for remote in remotes if checkout in remote]
        matches = len(match)

        if matches == 0:
            self.log.debug(
                "No remote branch tracking %s. These remote "
                "branches were found in "
                "the repository: %s." % (checkout, remotes))

        if matches > 1:
            raise RuntimeError(
                "Several remote branches %s for %s" % (remotes, checkout))

        remote = match[0]
        self.log.debug('branch %s -> %s', checkout, remote)
        return remote

    def tags(self):
        """ :return: The tags specified for the repository """
        return self.git.tags(cwd=self.giit_clone_path)

    def load_json_config(self):

        if self.workingtree_path:
            json_config = os.path.join(self.workingtree_path, 'giit.json')

            self.log.info("Using giit.json from %s workingtree",
                          self.workingtree_path)

            with open(json_config, 'r') as config_file:
                return json.load(config_file)

        # We only support building branches remote branches. The reason for
        # this it that it makes it easier to know what is the state of a given
        # branch. Two users might be on the same branch but have different
        # changes. Since we only build the remote we force users to push their
        # changes and thereby we have one source of truth of what is on a given
        # branch. Namely what has been pushed to the remote. Lets get the
        # corresponding remote branch

        # Make sure we start on the source branch, we may
        # read the giit.json file from here
        self.git.checkout(branch=self.giit_branch, cwd=self.giit_clone_path)

        json_config = os.path.join(self.giit_clone_path, 'giit.json')

        self.log.info("Using giit.json from %s branch", self.giit_branch)

        with open(json_config, 'r') as config_file:
            return json.load(config_file)

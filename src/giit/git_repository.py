import os
import hashlib


class GitRepository(object):

    def __init__(self, git, git_url_parser, clone_path,
                 source_branch, log):
        """ Create a new instance.

        :param git: The Git object used to run git commands.
        :param git_url_parser: Parser to extract information from
            the git URL
        :param clone_path: The user specified where clones should
            be made
        :param source_branch: An optional source branch. If specified
            this branch will be used as the source_branch otherwise
            we either the current branch or master.
        :param log: A logging object
        """
        self.git = git
        self.git_url_parser = git_url_parser
        self.clone_path = clone_path
        self.source_branch = source_branch
        self.log = log

        # The following attributes are specified after cloning:

        # Path to the local working tree (if one exists)
        self.workingtree_path = None

        # Path to where this repository is cloned
        self.repository_path = None

        # A unique name computed based on the git URL
        self.unique_name = None

    def clone(self, repository):
        """ Clones the repository.

        :param repository: The repository can either be an URL
            or a path to an existing repository
        """

        assert repository

        self._ensure_clone_path()

        # Get the URL to the repository
        if os.path.isdir(repository):
            self.workingtree_path = os.path.abspath(
                os.path.expanduser(repository))

            git_url = self.git.remote_origin_url(cwd=repository)

            if not self.source_branch:
                # If we don't have a source branch we use the one which is
                # currently checked out in the working tree
                self.source_branch, _ = self.git.branch(cwd=repository)
        else:
            git_url = repository

            if not self.source_branch:
                # If we don't have a source branch we use 'master
                self.source_branch = 'master'

        # Select the clone URL
        if self.workingtree_path:
            clone_url = self.workingtree_path
        else:
            clone_url = git_url

        self.log.info("Using git repository: %s", clone_url)

        # Compute the clone path
        git_info = self.git_url_parser.parse(url=git_url)

        url_hash = hashlib.sha1(git_url.encode('utf-8')).hexdigest()[:6]
        self.unique_name = git_info.name + '-' + url_hash

        if self.workingtree_path:
            self.unique_name = self.unique_name + '-local'

        self.repository_path = os.path.join(self.clone_path, self.unique_name)

        # Get the updates
        if os.path.isdir(self.repository_path):
            self.log.info('Running: git fetch in %s', self.repository_path)
            self.git.fetch(cwd=self.repository_path, all=True)
        else:
            self.log.info('Running: git clone in %s', self.repository_path)
            self.git.clone(repository=clone_url,
                           directory=self.repository_path, cwd=self.clone_path)

        # Make sure we start on the source branch, we may
        # read the giit.json file from here
        self.git.checkout(branch=self.source_branch,
                          cwd=self.repository_path)

        self.git.pull(cwd=self.repository_path)

    def tags(self):
        """ :return: The tags specified for the repository """
        return self.git.tags(cwd=self.repository_path)

    def _ensure_clone_path(self):
        """ Make sure the directory for the clones exist """
        self.clone_path = os.path.abspath(
            os.path.expanduser(self.clone_path))

        if not os.path.isdir(self.clone_path):
            os.makedirs(self.clone_path)

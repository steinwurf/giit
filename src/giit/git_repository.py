import os
import hashlib


class GitRepository(object):

    def __init__(self, git, git_url_parser, clone_path,
                 remote_branch, log):
        """ Create a new instance.

        :param git: The Git object used to run git commands.
        :param git_url_parser: Parser to extract information from
            the git URL
        :param clone_path: The user specified where clones should
            be made
        :param remote_branch: An optional source branch. If specified
            this branch will be used as the remote_branch otherwise
            we either the current branch or master.
        :param log: A logging object
        """
        self.git = git
        self.git_url_parser = git_url_parser
        self.clone_path = clone_path
        self.remote_branch = remote_branch
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

        version = self.git.version(cwd=self.clone_path)

        self.log.info("Using git version: %s",
                      ".".join([str(i) for i in version]))

        # Get the URL to the repository
        git_url = self._git_url(repository=repository)

        # Do we have a workingtree?
        if os.path.isdir(repository):
            self.workingtree_path = os.path.abspath(
                os.path.expanduser(repository))

        # Get the remote branch
        if not self.remote_branch:
            self.remote_branch = self._get_remote_branch(repository=repository)

        self.log.info("Using git repository: %s", git_url)

        # Compute the clone path
        git_info = self.git_url_parser.parse(url=git_url)

        url_hash = hashlib.sha1(git_url.encode('utf-8')).hexdigest()[:6]
        self.unique_name = git_info.name + '-' + url_hash

        self.repository_path = os.path.join(self.clone_path, self.unique_name)

        # Get the updates
        if os.path.isdir(self.repository_path):
            self.log.info('Running: git fetch in %s', self.repository_path)
            self.git.fetch(cwd=self.repository_path, all=True, prune=True)
        else:
            self.log.info('Running: git clone in %s', self.repository_path)
            self.git.clone(repository=git_url,
                           directory=self.repository_path,
                           cwd=self.clone_path)

        # Make sure we start on the source branch, we may
        # read the giit.json file from here
        self.git.checkout(branch=self.remote_branch,
                          cwd=self.repository_path)

    def tags(self):
        """ :return: The tags specified for the repository """
        return self.git.tags(cwd=self.repository_path)

    def _ensure_clone_path(self):
        """ Make sure the directory for the clones exist """
        self.clone_path = os.path.abspath(
            os.path.expanduser(self.clone_path))

        if not os.path.isdir(self.clone_path):
            os.makedirs(self.clone_path)

    def _git_url(self, repository):
        """ :return: The git URL """

        if os.path.isdir(repository):
            return self.git.remote_origin_url(cwd=repository)
        else:
            return repository

    def _get_remote_branch(self, repository):
        """ :return: The git URL """

        if os.path.isdir(repository):

            current = self.git.current_branch(cwd=repository)
            remotes = self.git.remote_branches(cwd=repository)

            match = [remote for remote in remotes if current in remote]
            matches = len(match)

            if matches == 0:
                raise RuntimeError(
                    "No remote branch tracking %s. These remote "
                    "branches were found in "
                    "the repository: %s.\nYou probably just need to "
                    "push the branch you are working on:\n\n"
                    "\tgit push -u origin %s\n" % (current, remotes, current))
            if matches > 1:
                raise RuntimeError(
                    "Several remote branches %s for %s" % (remotes, current))

            remote = match[0]
            self.log.debug('branch %s -> %s', current, remote)
            return remote

        else:
            return 'origin/master'

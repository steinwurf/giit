import os
import hashlib
import json


class GitRepository(object):

    def __init__(self, git, git_url_parser, clone_path, log, repository):
                 # source_branch, log):
        """ Create a new instance.

        :param git: The Git object used to run git commands.
        :param git_url_parser: Parser to extract information from
            the git URL
        :param clone_path: The user specified where clones should
            be made
        :param remote_branch: An optional source branch. If specified
            this branch will be used, otherwise we use either the current
            branch or master.
        :param log: A logging object
        """
        self.git = git
        self.git_url_parser = git_url_parser
        self.clone_path = os.path.abspath(os.path.expanduser(clone_path))
        self.log = log
        self.repository = repository

    @property
    def workingtree_path(self):
        if os.path.isdir(self.repository):
            return os.path.abspath(os.path.expanduser(self.repository))
        else:
            return None

    @property
    def git_url(self):
        if os.path.isdir(self.repository):
            return self.git.remote_origin_url(cwd=self.repository)
        else:
            return self.repository

    @property
    def unique_name(self):
        # Compute the clone path
        git_info = self.git_url_parser.parse(url=self.git_url)

        url_hash = hashlib.sha1(self.git_url.encode('utf-8')).hexdigest()[:6]
        return git_info.name + '-' + url_hash

    @property
    def giit_clone_path(self):
        return os.path.join(self.clone_path, self.unique_name)

    @property
    def giit_branch(self):

        if self.workingtree_path:
            current = self.git.current_branch(cwd=self.workingtree_path)
        else:
            current = "master"

        remotes = self.git.remote_branches(cwd=self.giit_clone_path)

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

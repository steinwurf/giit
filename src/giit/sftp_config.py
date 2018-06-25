import os


class SFTPConfig(object):

    def __init__(self, config):
        """ Initialize the config.

        :param config: Dict with all the config values initialized.
        """
        self.config = config

    def __getattr__(self, attribute):
        """ Allow config.attribute access.

        :return: The value of the attribute
        """
        return self[attribute]

    def __getitem__(self, key):
        """ Allow config.key access.

        :return: The value of the attribute
        """
        if not key in self.config:
            raise AttributeError("{} not found, keys are {}".format(
                key, self.config.keys()))

        return self.config[key]

    def __contains__(self, attribute):
        """ Checks if the attribute is available.
        :return: True if the attribute is available otherwise False
        """
        return attribute in self.config

    @staticmethod
    def from_dict(config):
        """ Take a user provided dict and ensure the correct keys are there

        :return A SFTPConfig object with the valid key
        """

        # Mandatory
        assert config['type'] == 'sftp'
        assert 'username' in config and config['username']
        assert 'hostname' in config and config['hostname']
        assert 'remote_path' in config and config['remote_path']
        assert 'local_path' in config and config['local_path']

        # Optional
        if not 'exclude_patterns' in config:
            config['exclude_patterns'] = []

        if not 'scope' in config:
            config['scope'] = ['source_branch']

        if not 'tag_semver_filter' in config:
            config['tag_semver_filter'] = None

        if not 'variables' in config:
            config['variables'] = ''

        return SFTPConfig(config=config)

import os


class SFTPConfig(object):

    def __init__(self, config):
        """ Create a new instance.

        :param config: A valid SFTPConfig as a dict.
        """
        self.config = config

    def __getattr__(self, attribute):
        """ Access an entry in the config.

        :param attribute: The entry to access as a string
        """

        if not attribute in self.config:
            raise AttributeError("Not found")

        return self.config[attribute]

    def __getitem__(self, key):
        """ Access an entry in the config.

        :param key: The entry to access as a string
        """

        if not key in self.config:
            raise AttributeError("Not found")

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

        if not 'variables' in config:
            config['variables'] = ''

        return SFTPConfig(config=config)

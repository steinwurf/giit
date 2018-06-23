import os


class PushConfig(object):

    def __init__(self, config):
        """ Create a new instance.

        :param config: A valid PushConfig as a dict.
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
        assert config['type'] == 'push'
        assert 'git_url' in config and config['git_url']
        assert 'target_branch' in config and config['target_branch']
        assert 'from_path' in config and config['from_path']

        # Optional
        if not 'commit_name' in config:
            config['commit_name'] = 'Giit Bot'

        if not 'commit_email' in config:
            config['commit_email'] = 'push@giit.bot'

        if not 'exclude_patterns' in config:
            config['exclude_patterns'] = []

        if not 'scope' in config:
            config['scope'] = ['source_branch']

        if not 'variables' in config:
            config['variables'] = ''

        if not 'from_path' in config:
            config['from_path'] = '${build_path}'

        if not 'to_path' in config:
            config['to_path'] = '/'

        return PushConfig(config=config)

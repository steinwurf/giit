#!/usr/bin/env python
# encoding: utf-8

import giit.config
import giit.variables_reader
import giit.compat


class ConfigReader(object):
    def __init__(self, config, context):
        """Create a new config reader.

        :param config: Config object containing the config
        :param context: Dict containing the context
        """
        self.config = config
        self.variables = giit.variables_reader.VariablesReader(
            variables=config["variables"], context=context
        )

    def __getattr__(self, attribute):

        if not attribute in self.config:
            raise AttributeError("Attribute %s not in config" % attribute)

        element = self.config[attribute]

        return self._expand(element=element)

    def _expand(self, element):

        if isinstance(element, giit.compat.string_type):
            return self.variables.expand(element=element)

        if isinstance(element, list):

            values = []
            for e in element:
                values.append(self._expand(element=e))

            return values

        return element

    def to_dict(self):

        output = {}

        def visit(value):
            if isinstance(value, dict):
                for k, v in value.items():
                    value[k] = visit(v)

            return value

        output

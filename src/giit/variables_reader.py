import string
import os


class VariablesReader(object):

    def __init__(self, variables, context):
        self.variables = variables
        self.context = context

    def _find_item(self, key):

        scope = self.context['scope']
        checkout = self.context['checkout']

        # We first look in the variables dict using the following order:
        #
        # 1. scope:checkout:variable
        # 2. scope:variable
        # 3. variable
        explicit = ':'.join([scope, checkout, key])

        if explicit in self.variables:
            return self.variables[explicit]

        partial = ':'.join([scope, key])

        if partial in self.variables:
            return self.variables[partial]

        if key in self.variables:
            return self.variables[key]

        # Check if the variable is defined in the context
        if key in self.context:
            return self.context[key]

        raise AttributeError("Not found {}".format(key))

    def __getitem__(self, key):

        variable = self._find_item(key=key)
        return string.Template(variable).substitute(self)

    def expand(self, element):

        return string.Template(element).substitute(self)

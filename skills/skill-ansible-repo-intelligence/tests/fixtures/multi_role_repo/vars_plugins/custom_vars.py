from ansible.plugins.vars import BaseVarsPlugin


class VarsModule(BaseVarsPlugin):
    def get_vars(self, loader, path, entities):
        result = {}
        result['custom_injected'] = 1
        result['custom_topology'] = 2
        return result

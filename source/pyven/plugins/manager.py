import sys, os

from pyven.exceptions.exception import PyvenException

class PluginsManager(object):
    DIR = os.path.join(os.environ.get('PVN_HOME'), 'plugins')

    def __init__(self):
        self.plugins = {}
        self.modules = {}
      
    @staticmethod
    def plugin_filename(name, version):
        return name + '-plugin_' + version + '.zip'
    
    def load(self):
        for name, version in self.plugins.items():
            plugin_file = os.path.join(PluginsManager.DIR, PluginsManager.plugin_filename(name, version))
            if not os.path.isfile(plugin_file):
                raise PyvenException('Unable to find plugin : ' + plugin_file)
            sys.path.append(plugin_file)
            self.modules[name] = __import__(name + '_plugin.parser', globals(), locals(), ['get'], 0)
            
    def get_parser(self, name, cwd):
        if name not in self.modules.keys():
            raise PyvenException('Plugin not available : ' + name)
        return self.modules[name].get(cwd)
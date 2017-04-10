import pyven.constants

class Project:
    
    def __init__(self, path, plugins={}):
        self.path = path
        self.constants = {}
        self.repositories = {}
        self.artifacts = {}
        self.packages = {}
        self.preprocessors = []
        self.builders = []
        self.postprocessors = []
        self.unit_tests = []
        self.integration_tests = []
        self.status = pyven.constants.STATUS[2]
        self.plugins = plugins
        
    def replace_constants(self, str):
        for name, value in self.constants.items():
            str = str.replace('$('+name+')', value)
        return str

import os

from pyven.processing.tests.test import Test

class IntegrationTest(Test):

    def __init__(self, cwd, type, report, path, filename, arguments, format, package):
        super(IntegrationTest,self).__init__(cwd, type, report, path, filename, arguments, format)
        self.package = package
        
    def _copy_resources(self, repo=None, resources=None):
        self.package.unpack(self.cwd, repo, flatten=True)

    def report_identifiers(self):
        return ['Integration', 'test', os.path.join(self.cwd, self.filename)]
    
import os

from pyven.processing.tests.test import Test

class UnitTest(Test):

    def __init__(self, cwd, type, report, path, filename, arguments, format):
        super(UnitTest,self).__init__(cwd, type, report, path, filename, arguments, format)

    def report_identifiers(self):
        return ['Unit', 'test', os.path.join(self.cwd, self.filename)]
    
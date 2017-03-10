import subprocess, os, time

from pyven.exceptions.exception import PyvenException

from pyven.processing.tests.test import Test

from pyven.logging.logger import Logger

class IntegrationTest(Test):

	def __init__(self, type, path, filename, arguments, format, package):
		super(IntegrationTest,self).__init__(type, path, filename, arguments, format)
		self.package = package
		
	def _copy_resources(self, repo=None, resources=None):
		self.package.unpack(self.path, repo, flatten=True)

	def report_identifiers(self):
		return ['Integration', 'test', os.path.join(self.path, self.filename)]
	
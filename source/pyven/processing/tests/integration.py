import subprocess, logging, os, time

from pyven.exceptions.exception import PyvenException

from pyven.processing.tests.test import Test

logger = logging.getLogger('global')

class IntegrationTest(Test):

	def __init__(self, node):
		super(IntegrationTest,self).__init__(node)
		packages = node.xpath('package')
		if len(packages) < 1:
			raise PyvenException('Missing package for test : ' + os.path.join(self.path, self.filename))
		if len(packages) > 1:
			raise PyvenException('Too many packages specified for test : ' + os.path.join(self.path, self.filename))
		self.package = packages[0].text
		
	def _copy_resources(self, repo=None, resources=None):
		self.package.unpack(self.path, repo, flatten=True)

	def report_identifiers(self):
		return ['Integration', 'test', os.path.join(self.path, self.filename)]
	
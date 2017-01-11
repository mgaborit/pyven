import subprocess, logging, os, time

from pyven.exceptions.exception import PyvenException

from pyven.processing.tests.test import Test

logger = logging.getLogger('global')
	
class UnitTest(Test):

	def __init__(self, node):
		super(UnitTest,self).__init__(node)

	def report_identifiers(self):
		return ['Unit', 'test', os.path.join(self.path, self.filename)]
	
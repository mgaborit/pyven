import subprocess, os, time

from pyven.exceptions.exception import PyvenException

from pyven.processing.tests.test import Test

from pyven.logging.logger import Logger

class UnitTest(Test):

	def __init__(self, type, path, filename, arguments, format):
		super(UnitTest,self).__init__(type, path, filename, arguments, format)

	def report_identifiers(self):
		return ['Unit', 'test', os.path.join(self.path, self.filename)]
	
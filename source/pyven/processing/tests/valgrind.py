import subprocess, os, time

from pyven.exceptions.exception import PyvenException

from pyven.processing.tests.test import Test

from pyven.logging.logger import Logger

class ValgrindTest(Test):

	def __init__(self, type, path, filename, arguments, format):
		super(ValgrindTest,self).__init__(type, path, filename, arguments, format)

	def report_identifiers(self):
		return ['Valgrind', 'memory', 'test', os.path.join(self.path, self.filename)]
	
	def _format_report_name(self):
		return self.filename+'-valgrind.xml'
	
	def _format_call(self):
		if os.name == 'posix':
			call = ['valgrind']
			for argument in self.arguments:
				call.append(argument)
			call.append('--xml=yes')
			call.append('--xml-file="'+self._format_report_name()+'"')
			call.append('./' + self.filename)
			call = [' '.join(call)]
			Logger.get().info(call)
			return call
		Logger.get().error('Trying to execute Valgrind on a non-Linux platform')

import subprocess, logging, os, time

from pyven.exceptions.exception import PyvenException

from pyven.processing.tests.test import Test

logger = logging.getLogger('global')
	
class ValgrindTest(Test):

	def __init__(self, node):
		super(ValgrindTest,self).__init__(node)

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
			logger.info(call)
			return call
		logger.error('Trying to execute Valgrind on a non-Linux platform')

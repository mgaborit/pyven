import subprocess, logging, os, time

from pyven.exceptions.exception import PyvenException

from pyven.processing.processible import Processible
from pyven.reporting.reportable import Reportable

logger = logging.getLogger('global')

# pym.xml 'test' node
class Test(Processible, Reportable):
	AVAILABLE_TYPES = ['unit', 'integration']

	def __init__(self, node):
		Processible.__init__(self)
		Reportable.__init__(self)
		self.type = node.get('type')
		if self.type is None:
			raise PyvenException('Missing test type')
		if self.type not in Test.AVAILABLE_TYPES:
			raise PyvenException('Wrong test type : ' + self.type, 'Available types : ' + str(Test.AVAILABLE_TYPES))
		(self.path, self.filename) = os.path.split(node.find('file').text)
		self.arguments = []
		for argument in node.xpath('arguments/argument'):
			self.arguments.append(argument.text)
	
	def report_summary(self):
		return self.report_identifiers()

	def report_status(self):
		return self.status
		
	def report_properties(self):
		properties = []
		properties.append(('Duration', str(self.duration) + ' seconds'))
		return properties
	
	def _format_call(self):
		if os.name == 'nt':
			call = [self.filename]
		elif os.name == 'posix':
			call = ['./' + self.filename]
		for argument in self.arguments:
			call.append(argument)
		return call

	def _copy_resources(self, repo=None):
		pass
		
	def process(self, verbose=False, repo=None):
		if not os.path.isfile(os.path.join(self.path, self.filename)):
			raise PyvenException('Test file not found : ' + os.path.join(self.path, self.filename))
		self._copy_resources(repo)
		FNULL = open(os.devnull, 'w')
		cwd = os.getcwd()
		if os.path.isdir(self.path):
			logger.info('Entering test directory : ' + self.path)
			os.chdir(self.path)
			logger.info('Running test : ' + self.filename)
			
			self.duration, out, err, returncode = self._call_command(self._format_call())
		
			os.chdir(cwd)
			
			if verbose:
				for line in out.splitlines():
					logger.info(line)
				for line in err.splitlines():
					logger.info(line)
				
			if returncode != 0:
				self.status = Processible.STATUS['failure']
				self.errors = Reportable.parse_logs(out.splitlines(), ['assertion', 'error'], [])
				logger.error('Test failed : ' + self.filename)
			else:
				self.status = Processible.STATUS['success']
				logger.info('Test OK : ' + self.filename)
			return returncode == 0
		logger.error('Unknown directory : ' + self.path)
		return False

	
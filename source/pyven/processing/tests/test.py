import subprocess, os, time

from pyven.exceptions.exception import PyvenException

from pyven.processing.processible import Processible
from pyven.reporting.reportable import Reportable

from pyven.logging.logger import Logger

class Test(Processible, Reportable):
	AVAILABLE_TYPES = ['unit', 'integration', 'valgrind']

	def __init__(self, type, path, filename, arguments, format):
		Processible.__init__(self)
		Reportable.__init__(self)
		self.type = type
		self.path = path
		self.filename = filename
		self.arguments = arguments
		self.format = format
	
	def title(self):
		return self.type + ' test : ' + os.path.join(self.path, self.filename)
		
	def properties(self):
		properties = {}
		properties['Status'] = self.status
		properties['Duration'] = str(self.duration) + ' seconds'
		return properties
	
	def _format_report_name(self):
		return self.filename+'-'+self.type+'.xml'
	
	def _format_call(self):
		if os.name == 'nt':
			call = [self.filename]
			call.append(self._format_report_name())
		elif os.name == 'posix':
			call = ['./'+self.filename+' '+self._format_report_name()]
		for argument in self.arguments:
			call.append(argument)
		Logger.get().info(' '.join(call))
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
			Logger.get().info('Entering test directory : ' + self.path)
			os.chdir(self.path)
			Logger.get().info('Running test : ' + self.filename)
			
			self.duration, out, err, returncode = self._call_command(self._format_call())
		
			os.chdir(cwd)
			
			if verbose:
				for line in out.splitlines():
					Logger.get().info(line)
				for line in err.splitlines():
					Logger.get().info(line)
			
			if returncode != 0:
				self.status = Processible.STATUS['failure']
				if os.path.isfile(os.path.join(self.path, self._format_report_name())):
					self.errors = Reportable.parse_xml(self.format, os.path.join(self.path, self._format_report_name()))
				else:
					Logger.get().error('Could not find XML test report = '+os.path.join(self.path, self._format_report_name()))
				Logger.get().error('Test failed : ' + self.filename)
			else:
				self.status = Processible.STATUS['success']
				Logger.get().info('Test OK : ' + self.filename)
			return returncode == 0
		Logger.get().error('Unknown directory : ' + self.path)
		return False

	
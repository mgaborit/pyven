import subprocess, os, time

import pyven.constants
from pyven.exceptions.exception import PyvenException

from pyven.processing.processible import Processible
from pyven.reporting.reportable import Reportable
from pyven.reporting.content.property import Property
from pyven.results.xml_parser import XMLParser

from pyven.logging.logger import Logger

class Test(Processible, Reportable):
	AVAILABLE_TYPES = ['unit', 'integration', 'valgrind']

	def __init__(self, type, report, path, filename, arguments, format):
		Processible.__init__(self)
		Reportable.__init__(self, report)
		self.type = type
		self.path = path
		self.filename = filename
		self.arguments = arguments
		self.parser = XMLParser(format)
	
	def title(self):
		if self.report is not None:
			return self.report
		return self.type + ' test'
		
	def properties(self):
		properties = []
		properties.append(Property(name='Executable', value=os.path.join(self.path, self.filename)))
		properties.append(Property(name='Duration', value=str(self.duration) + ' seconds'))
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
			
			self.parser.parse(os.path.join(self.path, self._format_report_name()))
			if returncode != 0:
				self.status = pyven.constants.STATUS[1]
				if os.path.isfile(os.path.join(self.path, self._format_report_name())):
					self.errors = self.parser.errors
				else:
					msg = 'Could not find XML report --> '+os.path.join(self.path, self._format_report_name())
					self.errors.append([msg])
					Logger.get().error(msg)
				Logger.get().error('Test failed : ' + self.filename)
			else:
				self.status = pyven.constants.STATUS[0]
				Logger.get().info('Test OK : ' + self.filename)
			return returncode == 0
		Logger.get().error('Unknown directory : ' + self.path)
		return False

	
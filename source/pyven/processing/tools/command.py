import subprocess, os, shutil, time

import pyven.constants
from pyven.exceptions.exception import PyvenException

from pyven.processing.processible import Processible
from pyven.processing.tools.tool import Tool
from pyven.reporting.reportable import Reportable
from pyven.reporting.content.property import Property

from pyven.logging.logger import Logger

class CommandTool(Tool):

	def __init__(self, type, name, scope, command, directory):
		super(CommandTool, self).__init__(type, name, scope)
		self.command = command
		self.directory = directory
	
	def title(self):
		return 'Command line'
		
	def properties(self):
		properties = []
		properties.append(Property(name='Command', value=self.command))
		properties.append(Property(name='Workspace', value=self.directory))
		properties.append(Property(name='Duration', value=str(self.duration) + ' seconds'))
		return properties
	
	def _format_call(self):
		call = []
		if pyven.constants.PLATFORM == 'linux':
			call.append('sh')
		call.extend(self.command.split(' '))
		if pyven.constants.PLATFORM == 'linux':
			call = [' '.join(call)]
		Logger.get().info(self.command)
		return call
	
	def process(self, verbose=False, warning_as_error=False):
		Logger.get().info('Preprocessing : ' + self.type + ':' + self.name)
		if not os.path.isdir(self.directory):
			os.makedirs(self.directory)
		Logger.get().info('Entering directory : ' + self.directory)
		cwd = os.getcwd()
		os.chdir(self.directory)
		self.duration, out, err, returncode = self._call_command(self._format_call())
		os.chdir(cwd)
		
		if verbose:
			for line in out.splitlines():
				Logger.get().info('[' + self.type + ']' + line)
			for line in err.splitlines():
				Logger.get().info('[' + self.type + ']' + line)
		
		self.warnings = Reportable.parse_logs(out.splitlines(), ['Warning', 'warning'], [])
		
		if returncode != 0:
			self.status = pyven.constants.STATUS[1]
			self.errors = Reportable.parse_logs(out.splitlines(), ['Error', 'error'], [])
			Logger.get().error('Preprocessing failed : ' + self.type + ':' + self.name)
		else:
			self.status = pyven.constants.STATUS[0]
		return returncode == 0
	
	def clean(self, verbose=False):
		Logger.get().info('Cleaning : ' + self.type + ':' + self.name + ' --> Nothing to be done')
		return True
		
import subprocess, os, shutil, time

import pyven.constants
from pyven.exceptions.exception import PyvenException

from pyven.processing.processible import Processible
from pyven.processing.tools.tool import Tool
from pyven.reporting.reportable import Reportable

from pyven.logging.logger import Logger

class CommandTool(Tool):

	def __init__(self, type, name, scope, command, directory):
		super(CommandTool, self).__init__(type, name, scope)
		self.command = command
		self.directory = directory
	
	def report_summary(self):
		return ['Command', self.name]

	def report_identifiers(self):
		return ['Command', self.name]
	
	def report_properties(self):
		properties = []
		properties.append(('Command', self.command))
		properties.append(('Directory', self.directory))
		properties.append(('Duration', str(self.duration) + ' seconds'))
		return properties
	
	def _format_call(self):
		call = []
		#if pyven.constants.PLATFORM == 'windows':
		#	call.append('cmd')
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
			self.status = Processible.STATUS['failure']
			self.errors = Reportable.parse_logs(out.splitlines(), ['Error', 'error'], [])
			Logger.get().error('Preprocessing failed : ' + self.type + ':' + self.name)
		else:
			self.status = Processible.STATUS['success']
		return returncode == 0
	
	def clean(self, verbose=False):
		Logger.get().info('Cleaning : ' + self.type + ':' + self.name + ' --> Nothing to be done')
		return True
		
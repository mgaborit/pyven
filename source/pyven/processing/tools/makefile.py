import subprocess, os, shutil, time

import pyven.constants
from pyven.exceptions.exception import PyvenException

from pyven.processing.processible import Processible
from pyven.reporting.reportable import Reportable
from pyven.processing.tools.tool import Tool
from pyven.reporting.content.property import Property
from pyven.results.line_logs_parser import LineLogsParser

from pyven.logging.logger import Logger

class MakefileTool(Tool):

	def __init__(self, type, report, name, scope, workspace, rules, options):
		super(MakefileTool, self).__init__(type, report, name, scope)
		self.workspace = workspace
		self.rules = rules
		self.options = options
		self.parser = LineLogsParser(error_patterns=['Error', 'error', 'ERROR', 'Erreur', 'erreur', 'ERREUR'],\
									error_exceptions=[],\
									warning_patterns=['Warning', 'warning', 'WARNING', 'Avertissement', 'avertissement', 'AVERTISSEMENT'],\
									warning_exceptions=[])
		
	def title(self):
		if self.report is not None:
			return self.report
		return 'Makefile ' + self.name
		
	def properties(self):
		properties = []
		properties.append(Property(name='Workspace', value=self.workspace))
		properties.append(Property(name='Rules', value=str(self.rules)))
		properties.append(Property(name='Duration', value=self.duration + ' seconds'))
		return properties
	
	def _format_call(self, clean=False):
		call = ['make']
		if clean:
			call.append('clean')
		else:
			for option in self.options:
				call.append(option)
			for rule in self.rules:
				call.append(rule)
		Logger.get().info(' '.join(call))
		return call
	
	def process(self, verbose=False, warning_as_error=False):
		Logger.get().info('Building : ' + self.type + ':' + self.name)
		cwd = os.getcwd()
		if os.path.isdir(self.workspace):
			Logger.get().info('Entering test directory : ' + self.workspace)
			os.chdir(self.workspace)
			Logger.get().info('Building : ' + self.type + ':' + self.name)
			self.duration, out, err, returncode = self._call_command(self._format_call())
			os.chdir(cwd)
			
			if verbose:
				for line in out.splitlines():
					Logger.get().info('[' + self.type + ']' + line)
				for line in err.splitlines():
					Logger.get().info('[' + self.type + ']' + line)
			
			self.parser.parse(out.splitlines() + err.splitlines())
			self.warnings = self.parser.warnings
			
			if returncode != 0:
				self.status = pyven.constants.STATUS[1]
				self.parser.parse(out.splitlines() + err.splitlines())
				self.errors = self.parser.errors
				Logger.get().error('Build failed : ' + self.type + ':' + self.name)
			elif warning_as_error and len(self.warnings) > 0:
				self.status = pyven.constants.STATUS[1]
				Logger.get().error('Build failed : ' + self.type + ':' + self.name)
			else:
				self.status = pyven.constants.STATUS[0]
			return returncode == 0 and (not warning_as_error or len(self.warnings) == 0)
		Logger.get().error('Unknown directory : ' + self.workspace)
		return False
		
	def clean(self, verbose=False):
		cwd = os.getcwd()
		Logger.get().info('Entering directory : ' + self.workspace)
		if os.path.isdir(self.workspace):
			os.chdir(self.workspace)
			if os.path.isfile('Makefile') or os.path.isfile('makefile'):
				Logger.get().info('Cleaning : ' + self.type + ':' + self.name)
				self.duration, out, err, returncode = self._call_command(self._format_call(clean=True))
				os.chdir(cwd)
				
				if verbose:
					for line in out.splitlines():
						Logger.get().info('[' + self.type + ']' + line)
					for line in err.splitlines():
						Logger.get().info('[' + self.type + ']' + line)
						
				if returncode != 0:
					Logger.get().error('Clean failed : ' + self.type + ':' + self.name)
				return returncode == 0
		Logger.get().info('No makefile found')
		return True
		
import subprocess, os, shutil, time

import pyven.constants
from pyven.exceptions.exception import PyvenException

from pyven.processing.processible import Processible
from pyven.processing.tools.tool import Tool
from pyven.reporting.reportable import Reportable
from pyven.reporting.content.property import Property
from pyven.results.line_logs_parser import LineLogsParser

from pyven.logging.logger import Logger

class MSBuildTool(Tool):

	def __init__(self, type, report, name, scope, configuration, architecture, project, options):
		super(MSBuildTool, self).__init__(type, report, name, scope)
		self.configuration = configuration
		self.architecture = architecture
		self.project = project
		self.options = options
		self.parser = LineLogsParser(error_patterns=['error', 'Error', 'erreur', 'Erreur'],\
									error_exceptions=['Erreur interne'],\
									warning_patterns=['warning', 'Warning', 'avertissement', 'Avertissement'],\
									warning_exceptions=[])
		
	def title(self):
		if self.report is not None:
			return self.report
		return 'MSBuild'
		
	def properties(self):
		properties = []
		properties.append(Property(name='Project', value=os.path.basename(self.project)))
		properties.append(Property(name='Configuration', value=self.configuration))
		properties.append(Property(name='Platform', value=self.architecture))
		properties.append(Property(name='Duration', value=str(self.duration) + ' seconds'))
		return properties
	
	def report_summary(self):
		return ['MSBuild', os.path.basename(self.project), self.configuration, self.architecture]

	def report_identifiers(self):
		return ['MSBuild', os.path.basename(self.project)]
	
	def report_properties(self):
		properties = []
		properties.append(('Configuration', self.configuration))
		properties.append(('Platform', self.architecture))
		properties.append(('Duration', str(self.duration) + ' seconds'))
		return properties
	
	def _format_call(self, project, clean=False):
		call = ['msbuild.exe', project]
		call.append('/consoleLoggerParameters:NoSummary;ErrorsOnly;WarningsOnly')
		if project.endswith('.sln'):
			call.append('/m')
			call.append('/property:Configuration='+self.configuration)
			call.append('/property:Platform='+self.architecture)
			if clean:
				call.append('/t:clean')
		elif project.endswith('.dproj'):
			call.append('/p:config='+self.configuration)
			call.append('/p:platform='+self.architecture)
			if clean:
				call.append('/t:clean')
			else:
				call.append('/t:build')
		else:
			raise PyvenException('Project format not supported : ' + project, 'Supported formats : *.sln, *.dproj')
		for option in self.options:
			call.append(option)
			
		Logger.get().info(' '.join(call))
		return call
	
	def process(self, verbose=False, warning_as_error=False):
		Logger.get().info('Building : ' + self.type + ':' + self.name)
		self.duration, out, err, returncode = self._call_command(self._format_call(self.project))
		
		if verbose:
			for line in out.splitlines():
				Logger.get().info('[' + self.type + ']' + line)
			for line in err.splitlines():
				Logger.get().info('[' + self.type + ']' + line)
		
		self.parser.parse(out.splitlines())
		warnings = self.parser.warnings
		for w in warnings:
			self.warnings.append([w[0].replace(w[0].split()[-1], '')])
		
		if returncode != 0:
			self.status = pyven.constants.STATUS[1]
			errors = self.parser.errors
			for e in errors:
				if e[0].split()[-1].startswith('[') and e[0].split()[-1].endswith(']'):
					self.errors.append([e[0].replace(e[0].split()[-1], '')])
				else:
					self.errors.append([e[0]])
			Logger.get().error('Build failed : ' + self.type + ':' + self.name)
		elif warning_as_error and len(self.warnings) > 0:
			self.status = pyven.constants.STATUS[1]
			Logger.get().error('Build failed : ' + self.type + ':' + self.name)
		else:
			self.status = pyven.constants.STATUS[0]
		return returncode == 0 and (not warning_as_error or len(self.warnings) == 0)

	def clean(self, verbose=False):
		Logger.get().info('Cleaning : ' + self.type + ':' + self.name)
		if os.path.isfile(self.project):
			self.duration, out, err, returncode = self._call_command(self._format_call(self.project, clean=True))
			
			if verbose:
				for line in out.splitlines():
					Logger.get().info('[' + self.type + ']' + line)
				for line in err.splitlines():
					Logger.get().info('[' + self.type + ']' + line)
					
			if returncode != 0:
				Logger.get().error('Clean failed : ' + self.type + ':' + self.name)
			return returncode == 0
		Logger.get().info('No project to be cleaned : ' + self.project)
		return True
		
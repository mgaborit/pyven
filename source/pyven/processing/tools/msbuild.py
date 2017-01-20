import subprocess, os, logging, shutil, time

from pyven.exceptions.exception import PyvenException

from pyven.processing.processible import Processible
from pyven.processing.tools.tool import Tool
from pyven.reporting.reportable import Reportable

logger = logging.getLogger('global')

class MSBuildTool(Tool):

	def __init__(self, node, project):
		super(MSBuildTool, self).__init__(node)
		self.configuration = node.find('configuration').text
		self.architecture = node.find('architecture').text
		self.project = project
		self.options = []
		for option in node.xpath('options/option'):
			self.arguments.append(option.text)
		if self.scope == 'preprocess':
			logger.warning('MSBuild will be called during preprocessing but not build')
		
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
			
		logger.info(' '.join(call))
		return call
	
	def process(self, verbose=False, warning_as_error=False):
		logger.info('Building : ' + self.type + ':' + self.name)
		self.duration, out, err, returncode = self._call_command(self._format_call(self.project))
		
		if verbose:
			for line in out.splitlines():
				logger.info('[' + self.type + ']' + line)
			for line in err.splitlines():
				logger.info('[' + self.type + ']' + line)
		
		warnings = Reportable.parse_logs(out.splitlines(), ['Warning', 'warning', 'Avertissement', 'avertissement'], ['0 Avertissement(s)', '0 Warning(s)'])
		for w in warnings:
			self.warnings.append([w[0].replace(w[0].split()[-1], '')])
		
		if returncode != 0:
			self.status = Processible.STATUS['failure']
			errors = Reportable.parse_logs(out.splitlines(), ['Error', 'error', 'Erreur', 'erreur'], ['0 Erreur(s)', '0 Error(s)'])
			for e in errors:
				self.errors.append([e[0].replace(e[0].split()[-1], '')])
			logger.error('Build failed : ' + self.type + ':' + self.name)
		elif warning_as_error and len(warnings) > 0:
			self.status = Processible.STATUS['failure']
			logger.error('Build failed : ' + self.type + ':' + self.name)
		else:
			self.status = Processible.STATUS['success']
		return returncode == 0 and (not warning_as_error or len(warnings) == 0)

	def clean(self, verbose=False):
		logger.info('Cleaning : ' + self.type + ':' + self.name)
		if os.path.isfile(self.project):
			self.duration, out, err, returncode = self._call_command(self._format_call(self.project, clean=True))
			
			if verbose:
				for line in out.splitlines():
					logger.info('[' + self.type + ']' + line)
				for line in err.splitlines():
					logger.info('[' + self.type + ']' + line)
					
			if returncode != 0:
				logger.error('Clean failed : ' + self.type + ':' + self.name)
			return returncode == 0
		logger.info('No project to be cleaned : ' + self.project)
		return True
		
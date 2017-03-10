import subprocess, os, shutil, time

import pyven.constants
from pyven.exceptions.exception import PyvenException

from pyven.processing.processible import Processible
from pyven.processing.tools.tool import Tool
from pyven.reporting.reportable import Reportable

from pyven.logging.logger import Logger

class CMakeTool(Tool):

	def __init__(self, type, name, scope, generator, output_path, definitions):
		super(CMakeTool, self).__init__(type, name, scope)
		self.generator = generator
		self.output_path = output_path
		self.definitions = definitions
	
	def report_summary(self):
		return ['CMake', self.name, self.generator]

	def report_identifiers(self):
		return ['CMake', self.name]
	
	def report_properties(self):
		properties = []
		properties.append(('Generator', self.generator))
		properties.append(('Duration', str(self.duration) + ' seconds'))
		return properties
	
	def _format_call(self):
		call = [self.type, '-H.', '-B'+self.output_path, '-G']
		if pyven.constants.PLATFORM == 'windows':
			call.append(self.generator)
		elif pyven.constants.PLATFORM == 'linux':
			call.append('"'+self.generator+'"')
		for definition in self.definitions:
			call.append('-D'+definition)
		if pyven.constants.PLATFORM == 'linux':
			call = [' '.join(call)]
		Logger.get().info(' '.join(call))
		return call
	
	def process(self, verbose=False, warning_as_error=False):
		Logger.get().info('Preprocessing : ' + self.type + ':' + self.name)
		self.duration, out, err, returncode = self._call_command(self._format_call())
		
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
		Logger.get().info('Cleaning : ' + self.type + ':' + self.name)
		if os.path.isdir(self.output_path):
			shutil.rmtree(self.output_path)
		return True
		
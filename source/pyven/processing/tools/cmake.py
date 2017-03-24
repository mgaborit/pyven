import subprocess, os, shutil, time

import pyven.constants
from pyven.exceptions.exception import PyvenException

from pyven.processing.processible import Processible
from pyven.processing.tools.tool import Tool
from pyven.reporting.reportable import Reportable
from pyven.reporting.content.property import Property
from pyven.results.block_logs_parser import BlockLogsParser

from pyven.logging.logger import Logger

class CMakeTool(Tool):

	def __init__(self, type, report, name, scope, generator, output_path, definitions):
		super(CMakeTool, self).__init__(type, report, name, scope)
		self.target_generator = generator
		self.output_path = output_path
		self.definitions = definitions
		self.parser = BlockLogsParser(begin_error_patterns=['-- Configuring incomplete, errors occurred!'],\
									end_error_patterns=[],\
									begin_warning_patterns=[],\
									end_warning_patterns=[])
	
	def title(self):
		if self.report is not None:
			return self.report
		return 'CMake ' + self.name
		
	def properties(self):
		properties = []
		properties.append(Property(name='Generator', value=self.target_generator))
		properties.append(Property(name='Duration', value=str(self.duration) + ' seconds'))
		return properties
	
	def _format_call(self):
		call = [self.type, '-H.', '-B'+self.output_path, '-G']
		if pyven.constants.PLATFORM == 'windows':
			call.append(self.target_generator)
		elif pyven.constants.PLATFORM == 'linux':
			call.append('"'+self.target_generator+'"')
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
		
		self.parser.parse(out.splitlines() + err.splitlines())
		self.warnings = self.parser.warnings
		
		if returncode != 0:
			self.status = pyven.constants.STATUS[1]
			self.errors = self.parser.errors
			Logger.get().error('Preprocessing failed : ' + self.type + ':' + self.name)
		else:
			self.status = pyven.constants.STATUS[0]
		return returncode == 0
	
	def clean(self, verbose=False):
		Logger.get().info('Cleaning : ' + self.type + ':' + self.name)
		if os.path.isdir(self.output_path):
			shutil.rmtree(self.output_path)
		return True
		
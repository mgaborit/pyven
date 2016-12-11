import subprocess, os, logging, shutil, time

from pyven.exceptions.exception import PyvenException

from pyven.processing.processible import Processible
from pyven.processing.tools.tool import Tool

logger = logging.getLogger('global')

class MakefileTool(Tool):

	def __init__(self, node):
		super(MakefileTool, self).__init__(node)
		workspaces = node.xpath('workspace')
		if len(workspaces) < 1:
			raise PyvenException('Missing Makefile directory')
		if len(workspaces) > 1:
			raise PyvenException('Too many Makefile directories specified, only one needed')
		self.workspace = workspaces[0].text
		self.options = []
		for option in node.xpath('options/option'):
			self.options.append(option.text)
		self.rules = []
		for rule in node.xpath('rules/rule'):
			self.rules.append(rule.text)
		if self.scope == 'preprocess':
			logger.warning('Makefile will be called during preprocessing but not build')
		
	def _format_call(self, clean=False):
		call = ['make']
		if clean:
			call.append('clean')
		else:
			for option in self.options:
				call.append(option)
			for rule in self.rules:
				call.append(rule)
			
		return call
	
	def process(self, verbose=False):
		FNULL = open(os.devnull, 'w')
		cwd = os.getcwd()
		logger.info('Entering test directory : ' + self.workspace)
		if os.path.isdir(self.workspace):
			os.chdir(self.workspace)
			logger.info('Building : ' + self.type + ':' + self.name)
			if verbose:
				return_code = subprocess.call(self._format_call())
			else:
				return_code = subprocess.call(self._format_call(), stdout=FNULL, stderr=subprocess.STDOUT)
			os.chdir(cwd)
			if return_code != 0:
				logger.error('Build failed : ' + self.type + ':' + self.name)
				return False
			self.steps[0]['status'] = Tool.STATUS['success']
			return True
		logger.error('Unknown directory : ' + self.workspace)
		return False
		
	def clean(self, verbose=False):
		FNULL = open(os.devnull, 'w')
		cwd = os.getcwd()
		logger.info('Entering test directory : ' + self.workspace)
		if os.path.isdir(self.workspace):
			os.chdir(self.workspace)
			logger.info('Cleaning : ' + self.type + ':' + self.name)
			if verbose:
				return_code = subprocess.call(self._format_call(clean=True))
			else:
				return_code = subprocess.call(self._format_call(clean=True), stdout=FNULL, stderr=subprocess.STDOUT)
			if return_code != 0:
				logger.error('Clean failed : ' + self.type + ':' + self.name)
				return False
			return True
		logger.error('Unknown directory : ' + self.workspace)
		return False
		
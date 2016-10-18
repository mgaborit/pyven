import logging, os

from lxml import etree

from artifact.artifact import Artifact
from tool.tool import Tool
from test.test import Test
from package.package import Package

logger = logging.getLogger('global')

class Project:
	def __init__(self, verbose=False):
		logger.info('Initializing Pyven project')
		
		self.verbose = verbose
		if os.name == 'nt':
			self.platform = 'windows'
		elif os.name == 'posix':
			self.platform = 'linux'
		logger.info('Project set for '+self.platform+' platform')
		
		self.artifacts = {}
		self.packages = {}
		self.tools = {"preprocessors" : [], "builders" : []}
		self.tests = []

	def clean(self):
		print 'clean'
	
	def _extract_artifacts(self, tree):
		for node in tree.xpath('/pyven/platform[@id="'+self.platform+'"]/artifacts/artifact'):
			artifact = Artifact.factory(node)
			if artifact.format_name() in self.artifacts.keys():
				logger.error('Artifact already added : ' + artifact.format_name())
			else:
				self.artifacts[artifact.format_name()] = artifact
				logger.info('Added artifact : ' + artifact.format_name())
	
	def _extract_tools(self, tree):
		for node in tree.xpath('/pyven/platform[@id="'+self.platform+'"]/build/tools/tool[@scope="preprocess"]'):
			preprocessor = Tool.factory(node)
			self.tools['preprocessors'].append(preprocessor)
			logger.info('Added preprocessor : ' + preprocessor.name + ':' + preprocessor.id)
		for node in tree.xpath('/pyven/platform[@id="'+self.platform+'"]/build/tools/tool[@scope="build"]'):
			builder = Tool.factory(node)
			self.tools['builders'].append(builder)
			logger.info('Added builder : ' + builder.name + ':' + builder.id)
	
	def _extract_tests(self, tree):
		for node in tree.xpath('/pyven/platform[@id="'+self.platform+'"]/tests/test'):
			test = Test(node)
			self.tests.append(test)
			logger.info('Added test : ' + os.path.join(test.path, test.filename))
	
	def _extract_packages(self, tree):
		for node in tree.xpath('/pyven/platform[@id="'+self.platform+'"]/packages/package'):
			package = Package(node)
			if package.format_name() in self.packages.keys():
				logger.error('Package already added : ' + package.format_name())
			else:
				for item in node.xpath('item'):
					if item.text in self.artifacts.keys():
						artifact = self.artifacts[item.text]
						package.items.append(artifact)
						logger.info('Added artifact ' + artifact.format_name() + ' to package ' + package.format_name())
					else:
						logger.error('Artifact not found : ' + item.text)
				self.packages[package.format_name()] = package
				logger.info('Added package : ' + package.format_name())
	
	def configure(self):
		logger.info('STEP CONFIGURE : STARTING')
		logger.info('Starting pym.xml parsing')
		tree = etree.parse('pym.xml')
		logger.info('PYM parsing successful')
		self._extract_artifacts(tree)
		self._extract_tools(tree)
		self._extract_tests(tree)
		self._extract_packages(tree)
		logger.info('STEP CONFIGURE : COMPLETED')

			
	def build(self):
		logger.info('STEP BUILD : STARTING')
		logger.info('Starting preprocessing')
		for tool in self.tools['preprocessors']:
			tool.process(self.verbose)
		logger.info('Preprocessing completed')
		logger.info('Starting build')
		for tool in self.tools['builders']:
			tool.process(self.verbose)
		logger.info('build completed')
		logger.info('STEP BUILD : COMPLETED')
		
		
	def test(self):
		logger.info('STEP TEST : STARTING')
		for test in self.tests:
			test.run(self.verbose)
		logger.info('STEP TEST : COMPLETED')
		
		
	def package(self):
		logger.info('STEP PACKAGE : STARTING')
		for package in self.packages.values():
			package.zip()
		logger.info('STEP PACKAGE : COMPLETED')
		
		
	def verify(self):
		logger.info('STEP VERIFY : STARTING')
		raise NotImplementedError('Invalid call')
		logger.info('STEP VERIFY : COMPLETED')
		
		
	def install(self):
		logger.info('STEP INSTALL : STARTING')
		raise NotImplementedError('Invalid call')
		logger.info('STEP INSTALL : COMPLETED')
		
		
	def deploy(self):
		logger.info('STEP DEPLOY : STARTING')
		raise NotImplementedError('Invalid call')
		logger.info('STEP DEPLOY : COMPLETED')

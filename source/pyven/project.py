import os
import logging

from lxml import etree

from artifact.artifact import Artifact
from tool.tool import Tool

logger = logging.getLogger('global')

class Project:
	def __init__(self):
		logger.info('Initializing Pyven project')
		
		if os.name == 'nt':
			self.platform = 'windows'
		elif os.name == 'posix':
			self.platform = 'linux'
		logger.info('Project set for '+self.platform+' platform')
		
		self.artifacts = []
		self.tools = {"preprocessors" : [], "builders" : []}

	def clean(self):
		print 'clean'
	
	def configure(self):
		logger.info('STEP CONFIGURE : STARTING')
		logger.info('Starting pym.xml parsing')
		tree = etree.parse('pym.xml')
		logger.info('pym.xml parsing successful')
		for artifact_node in tree.xpath('/pyven/platform[@id="'+self.platform+'"]/artifacts/artifact'):
			artifact = Artifact.factory(artifact_node)
			self.artifacts.append(artifact)
			logger.info('Added artifact : ' + artifact.group + ':' + artifact.id + ':' + artifact.version)
		
		for preprocessor_node in tree.xpath('/pyven/platform[@id="'+self.platform+'"]/build/tools/tool[@scope="preprocess"]'):
			preprocessor = Tool.factory(preprocessor_node)
			self.tools['preprocessors'].append(preprocessor)
			logger.info('Added preprocessor : ' + preprocessor.name + ':' + preprocessor.id)
		for builder_node in tree.xpath('/pyven/platform[@id="'+self.platform+'"]/build/tools/tool[@scope="build"]'):
			builder = Tool.factory(builder_node)
			self.tools['builders'].append(builder)
			logger.info('Added builder : ' + builder.name + ':' + builder.id)
		logger.info('STEP CONFIGURE : COMPLETED')

			
	def build(self):
		self.configure()
		logger.info('STEP BUILD : STARTING')
		logger.info('Starting preprocessing')
		for tool in self.tools['preprocessors']:
			tool.process()
		logger.info('Preprocessing completed')
		logger.info('Starting build')
		for tool in self.tools['builders']:
			tool.process()
		logger.info('build completed')
		logger.info('STEP BUILD : COMPLETED')
		
		
	def test(self):
		logger.info('STEP TEST : STARTING')
		raise NotImplementedError('Invalid call')
		logger.info('STEP TEST : COMPLETED')
		
		
	def package(self):
		logger.info('STEP PACKAGE : STARTING')
		raise NotImplementedError('Invalid call')
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

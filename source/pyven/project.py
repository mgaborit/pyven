import os

from lxml import etree

from artifact.artifact import Artifact
from tool.tool import Tool

class Project:

	def __init__(self):
		if os.name == 'nt':
			self.platform = 'windows'
		elif os.name == 'posix':
			self.platform = 'linux'
			
		self.artifacts = []
		self.tools = {"preprocessors" : [], "builders" : []}

	def clean(self):
		print 'clean'
	
	def configure(self):
		tree = etree.parse('pym.xml')
		for artifact_node in tree.xpath('/pyven/platform[@id="'+self.platform+'"]/artifacts/artifact'):
			self.artifacts.append(Artifact.factory(artifact_node))
		
		for preprocessor_node in tree.xpath('/pyven/platform[@id="'+self.platform+'"]/build/tools/tool[@scope="preprocess"]'):
			self.tools['preprocessors'].append(Tool.factory(preprocessor_node))
		
		for builder_node in tree.xpath('/pyven/platform[@id="'+self.platform+'"]/build/tools/tool[@scope="build"]'):
			self.tools['builders'].append(Tool.factory(builder_node))

	def build(self):
		for tool in self.tools['preprocessors']:
			tool.process()

		for tool in self.tools['builders']:
			tool.process()
		
	def test(self):
		print 'test'
		
	def package(self):
		print 'package'
		
	def verify(self):
		print 'verify'
		
	def install(self):
		print 'install'
		
	def deploy(self):
		print 'deploy'
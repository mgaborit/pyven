import os

from lxml import etree

from artifact.artifact import Artifact

class Project:

	def __init__(self):
		if os.name == 'nt':
			self.platform = 'windows'
		elif os.name == 'posix':
			self.platform = 'linux'
			
		self.artifacts = []

	def _parse_pym(self):
		tree = etree.parse('pym.xml')
		
		for artifact_node in tree.xpath('/pyven/platform[@id="'+self.platform+'"]/artifacts/artifact'):
			self.artifacts.append(Artifact.factory(artifact_node))
		
		for artifact in self.artifacts:
			print artifact.group + ':' + artifact.id + ':' + artifact.version + ':' + artifact.get()
	
	def clean(self):
		print 'clean'
	
	def configure(self):
		self._parse_pym()

	def build(self):
		print 'build'
		
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
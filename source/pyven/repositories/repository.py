import os, logging, shutil

from pyven.exceptions.exception import PyvenException

logger = logging.getLogger('global')

# pym.xml 'repository' node
class Repository(object):
	AVAILABLE_TYPES = ['file']
	
	def __init__(self, name, type, url):
		self.name = name
		if self.name is None:
			raise PyvenException('Missing repository name')
		self.type = type
		if self.type is None:
			raise PyvenException('Missing repository type')
		if self.type not in Repository.AVAILABLE_TYPES and self.type != 'workspace':
			raise PyvenException('Invalid repository type : ' + self.type, 'Available types : ' + str(Repository.AVAILABLE_TYPES))
		self.url = url
		if self.url is None:
			raise PyvenException('Missing repository url')

	@classmethod
	def from_node(cls, node):
		return cls(node.get('name'), node.get('type'), node.get('url'))

	def is_available(self):
		raise NotImplementedError
		
	def retrieve(self, artifact, destination):
		raise NotImplementedError
		
	def publish(self, artifact, source):
		raise NotImplementedError
import logging, os

logger = logging.getLogger('global')

class Item(object):

	def __init__(self, node):
		self.group = node.get('group')
		self.id = node.get('id')
		self.version = node.get('version')
		self.repo = node.get('repo')
		self.to_retrieve = self.repo is not None
	
	def format_name(self, separator=':'):
		return self.group + separator + self.id + separator + self.version
	
	def publish_location(self):
		return os.path.join(self.group, self.id, self.version)
	
	def type(self):
		raise NotImplementedError
	
	def basename(self):
		raise NotImplementedError
	
	def workspace_location(self, workspace):
		raise NotImplementedError

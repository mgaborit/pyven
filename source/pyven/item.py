import logging, os

logger = logging.getLogger('global')

class Item(object):

	def __init__(self, node):
		self.group = node.get('group')
		self.id = node.get('id')
		self.version = node.get('version')
	
	def format_name(self, separator=':'):
		return self.group + separator + self.id + separator + self.version
	
	def publish_location(self):
		return os.path.join(self.group, self.id, self.version)
	
	def type(self):
		raise NotImplementedError('Invalid call to "type" method')
	
	def basename(self):
		raise NotImplementedError('Invalid call to "basename" method')
	
	def workspace_location(self, workspace):
		raise NotImplementedError('Invalid call to "workspace_location" method')

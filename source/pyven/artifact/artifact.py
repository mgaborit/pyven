import logging

logger = logging.getLogger('global')

# pym.xml 'artifact' node
class Artifact(object):

	def __init__(self, node):
		self.group = node.get('group')
		self.id = node.get('id')
		self.version = node.get('version')
		self.file = ''
		if node.get('scope') == 'intern':
			self.file = node.find('file').text
		
	def format_name(self):
		return self.group + ':' + self.id + ':' + self.version

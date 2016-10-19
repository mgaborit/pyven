import logging, os

logger = logging.getLogger('global')

from item import Item

# pym.xml 'artifact' node
class Artifact(Item):

	def __init__(self, node):
		super(Artifact, self).__init__(node)
		self.file = None
		self.repo = node.get('repo')
		if self.repo is None:
			self.file = node.text
	
	def type(self):
		return 'artifact'
	
	def basename(self):
		if self.file is not None:
			return os.path.basename(self.file)
		else:
			logger.error('Unknown artifact location : ' + self.format_name())
		
	def workspace_location(self, workspace):
		return os.path.join(workspace, 'artifacts', self.publish_location())

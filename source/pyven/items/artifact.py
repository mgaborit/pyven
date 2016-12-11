import logging, os

from pyven.exceptions.exception import PyvenException

logger = logging.getLogger('global')

from pyven.items.item import Item

# pym.xml 'artifact' node
class Artifact(Item):

	def __init__(self, node):
		super(Artifact, self).__init__(node)
		self.file = None
		if not self.to_retrieve:
			self.file = node.text
	
	def type(self):
		return 'artifact'
	
	def basename(self):
		if self.file is not None:
			return os.path.basename(self.file)
		raise PyvenException('Unknown artifact location : ' + self.format_name())
	
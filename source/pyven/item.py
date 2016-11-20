import logging, os

from pyven.exception import PyvenException

logger = logging.getLogger('global')

class Item(object):

	def __init__(self, node):
		self.company = node.get('company')
		self.name = node.get('name')
		self.config = node.get('config')
		self.version = node.get('version')
		self.repo = node.get('repo')
		self.to_retrieve = self.repo is not None
	
	def format_name(self, separator=':'):
		return self.company + separator + self.name + separator + self.config + separator + self.version
	
	def type(self):
		raise NotImplementedError
	
	def basename(self):
		raise NotImplementedError
	
	def item_specific_location(self):
		return os.path.join(self.company, self.name, self.config, self.version)
	
	def repo_location(self, repo):
		return os.path.join(repo, self.type() + 's')

	def location(self, repo):
		return os.path.join(self.repo_location(repo), self.item_specific_location())
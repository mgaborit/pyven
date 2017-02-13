import logging, os
from pyven.exceptions.exception import PyvenException

logger = logging.getLogger('global')

class Item(object):
	if os.name == 'nt':
		PLATFORM = 'windows'
	elif os.name == 'posix':
		PLATFORM = 'linux'
	else:
		raise PyvenException('Unsupported platform')
	
	def __init__(self, company, name, config, version, repo, to_retrieve, publish):
		self.company = company
		self.name = name
		self.config = config
		self.version = version
		self.repo = repo
		self.to_retrieve = to_retrieve
		self.publish = publish
	
	def format_name(self, separator=':'):
		return self.company + separator + self.name + separator + self.config + separator + self.version
	
	def type(self):
		raise NotImplementedError
	
	def basename(self):
		raise NotImplementedError
	
	def item_specific_location(self):
		return os.path.join(Item.PLATFORM, self.company, self.name, self.config, self.version)
	
	def repo_location(self, repo):
		return os.path.join(repo, self.type() + 's')

	def location(self, repo):
		return os.path.join(self.repo_location(repo), self.item_specific_location())
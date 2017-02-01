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
	
	def __init__(self, node):
		self.company = node.get('company')
		if self.company is None:
			raise PyvenException('Missing artifact or package company')
		self.name = node.get('name')
		if self.name is None:
			raise PyvenException('Missing artifact or package name')
		self.config = node.get('config')
		if self.config is None:
			raise PyvenException('Missing artifact or package config')
		self.version = node.get('version')
		if self.version is None:
			raise PyvenException('Missing artifact or package version')
		self.repo = node.get('repo')
		self.to_retrieve = self.repo is not None
		if self.to_retrieve:
			self.publish = False
		else:
			self.publish = True
		publish = node.get('publish')
		if publish is not None:
			if publish == 'true':
				self.publish = True
			elif publish == 'false':
				self.publish = False
			else:
				raise PyvenException('Invalid value for "publish" attribute')
	
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
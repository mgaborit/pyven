import os, shutil

from pyven.exceptions.exception import PyvenException

class Repository(object):
	AVAILABLE_TYPES = ['file']
	
	def __init__(self, name, type, url, release=False):
		self.name = name
		self.type = type
		self.url = url
		self.release = release

	def is_reachable(self):
		raise NotImplementedError
		
	def is_available(self, item, type):
		raise NotImplementedError
		
	def retrieve(self, artifact, destination):
		raise NotImplementedError
		
	def publish(self, artifact, source):
		raise NotImplementedError
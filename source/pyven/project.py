import logging

logger = logging.getLogger('global')

class Project:
	
	def __init__(self, path):
		self.path = path
		self.constants = {}
		self.repositories = {}
		self.artifacts = {}
		self.packages = {}
		self.preprocessors = []
		self.builders = []
		self.unit_tests = []
		self.integration_tests = []
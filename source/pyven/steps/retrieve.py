import logging, os, shutil

from pyven.exceptions.exception import PyvenException
from pyven.exceptions.repository_exception import RepositoryException

from pyven.steps.step import Step
from pyven.steps.utils import retrieve
from pyven.checkers.checker import Checker

logger = logging.getLogger('global')

class Retrieve(Step):
	def __init__(self, path, verbose):
		super(Retrieve, self).__init__(path, verbose)
		self.name = 'retrieve'
		self.checker = Checker('Retrieval')
		self.repositories = {}
		self.artifacts = {}
		self.packages = {}

	@Step.error_checks
	def process(self):
		ok = retrieve('artifact', self, self.artifacts) and retrieve('package', self, self.packages)
		if retrieve('artifact', self, self.artifacts) and retrieve('package', self, self.packages):
			for package in [p for p in self.packages.values() if not p.to_retrieve]:
				for item in [i for i in package.items if i.to_retrieve]:
					for built_item in [i for i in package.items if not i.to_retrieve]:
						dir = os.path.dirname(built_item.file)
						if not os.path.isdir(dir):
							os.makedirs(dir)
						logger.info(self.log_path() + 'Copying artifact ' + item.format_name() + ' to directory ' + dir)
						shutil.copy(os.path.join(item.location(Step.WORKSPACE.url), item.basename()), os.path.join(dir, item.basename()))
		return ok
		
	
	
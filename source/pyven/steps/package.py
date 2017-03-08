import logging, time, os

from pyven.exceptions.exception import PyvenException
from pyven.exceptions.repository_exception import RepositoryException

from pyven.steps.step import Step
from pyven.checkers.checker import Checker

logger = logging.getLogger('global')

class Package(Step):
	def __init__(self, path, verbose):
		super(Package, self).__init__(path, verbose)
		self.name = 'package'
		self.checker = Checker('Packaging')
		self.repositories = {}
		self.artifacts = {}
		self.packages = {}

	def _retrieve(self, type, items):
		ok = True
		for item in [i for i in items.values() if i.to_retrieve and i.repo]:
			try:
				if not self.repositories[item.repo].is_reachable():
					if Step.WORKSPACE.is_available(item):
						item.file = os.path.join(item.location(Step.WORKSPACE.url), os.listdir(item.location(Step.WORKSPACE.url))[0])
						logger.info(self.log_path() + 'Workspace --> Retrieved ' + type + ' : ' + item.format_name())
					else:
						raise RepositoryException('Repository ' + item.repo + ' not accessible -->  Unable to retrieve ' + type + ' : ' + item.format_name())
				elif not self.repositories[item.repo].is_available(item):
					raise RepositoryException('Repository ' + item.repo + ' --> ' + type + ' ' + item.format_name() + ' not available')
				elif item.repo != Step.WORKSPACE.name:
					self.repositories[item.repo].retrieve(item, Step.WORKSPACE)
					logger.info(self.log_path() + 'Repository ' + item.repo + ' --> Retrieved ' + type + ' : ' + item.format_name())
				else:
					item.file = os.path.join(item.location(Step.WORKSPACE.url), os.listdir(item.location(Step.WORKSPACE.url))[0])
					logger.info(self.log_path() + 'Workspace --> Retrieved ' + type + ' : ' + item.format_name())
			except RepositoryException as e:
				self.checker.errors.append(e.args)
				for msg in e.args:
					logger.error(msg)
				ok = False
		return ok
		
	@Step.error_checks
	def process(self):
		ok = self._retrieve('artifact', self.artifacts) and self._retrieve('package', self.packages)
		if ok:
			for package in [p for p in self.packages.values() if not p.to_retrieve]:
				try:
					if not package.pack(Step.WORKSPACE):
						ok = False
				except PyvenException as e:
					self.checker.errors.append(e.args)
					for msg in e.args:
						logger.error(self.log_path() + msg)
					ok = False
		return ok
		
	
	
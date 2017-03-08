import logging, time, os

from pyven.exceptions.exception import PyvenException
from pyven.exceptions.repository_exception import RepositoryException

from pyven.steps.step import Step
from pyven.steps.utils import retrieve
from pyven.checkers.checker import Checker

logger = logging.getLogger('global')

class PackageStep(Step):
	def __init__(self, path, verbose):
		super(PackageStep, self).__init__(path, verbose)
		self.name = 'package'
		self.checker = Checker('Packaging')
		self.repositories = {}
		self.artifacts = {}
		self.packages = {}

	@Step.error_checks
	def process(self):
		ok = retrieve('artifact', self, self.artifacts) and retrieve('package', self, self.packages)
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
		
	
	
import logging, time, os

from pyven.exceptions.exception import PyvenException
from pyven.exceptions.repository_exception import RepositoryException

from pyven.steps.step import Step
from pyven.checkers.checker import Checker

logger = logging.getLogger('global')

class Install(Step):
	def __init__(self, path, verbose):
		super(Install, self).__init__(path, verbose)
		self.name = 'install'
		self.checker = Checker('Installation')
		self.artifacts = {}
		self.packages = {}

	@Step.error_checks
	def process(self):
		ok = True
		for artifact in [a for a in self.artifacts.values() if a.publish]:
			Step.LOCAL_REPO.publish(artifact, Step.WORKSPACE)
			logger.info(self.log_path() + 'Repository ' + Step.LOCAL_REPO.name + ' --> Published artifact ' + artifact.format_name())
		for package in [p for p in self.packages.values() if p.publish]:
			Step.LOCAL_REPO.publish(package, Step.WORKSPACE)
			logger.info(self.log_path() + 'Repository ' + Step.LOCAL_REPO.name + ' --> Published package ' + package.format_name())
		return ok
		
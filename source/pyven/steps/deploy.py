import logging, time, os

from pyven.exceptions.exception import PyvenException
from pyven.exceptions.repository_exception import RepositoryException

from pyven.steps.step import Step
from pyven.checkers.checker import Checker

logger = logging.getLogger('global')

class Deploy(Step):
	def __init__(self, path, verbose, release):
		super(Deploy, self).__init__(path, verbose)
		self.name = 'deploy'
		self.checker = Checker('Deployment')
		self.release = release
		self.repositories = {}
		self.artifacts = {}
		self.packages = {}

	@Step.error_checks
	def process(self):
		ok = True
		repositories = [r for r in self.repositories.values() if (not r.release or (r.release and self.release)) and r.name != Step.WORKSPACE.name]
		for repo in repositories:
			if not repo.is_reachable():
				msg = self.log_path() + 'Repository ' + repo.name + ' --> unreachable for deployment'
				logger.error(msg)
				self.checker.errors.append([msg])
				ok = False
		if ok:
			for repo in repositories:
				try:
					for artifact in [a for a in self.artifacts.values() if a.publish]:
						repo.publish(artifact, Step.WORKSPACE)
						logger.info(self.log_path() + 'Repository ' + repo.name + ' --> Published artifact ' + artifact.format_name())
					for package in [p for p in self.packages.values() if p.publish]:
						repo.publish(package, Step.WORKSPACE)
						logger.info(self.log_path() + 'Repository ' + repo.name + ' --> Published package ' + package.format_name())
				except RepositoryException as e:
					self.checkers['deployment'].errors.append(e.args)
					for msg in e.args:
						logger.error(self.log_path() + msg)
					raise e
		return ok
		
	
	
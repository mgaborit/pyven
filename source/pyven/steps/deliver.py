import logging, time, os

from pyven.exceptions.exception import PyvenException
from pyven.exceptions.repository_exception import RepositoryException

from pyven.steps.step import Step
from pyven.checkers.checker import Checker

logger = logging.getLogger('global')

class Deliver(Step):
	def __init__(self, path, verbose, location):
		super(Deliver, self).__init__(path, verbose)
		self.name = 'deliver'
		self.checker = Checker('Delivery')
		self.location = location
		self.repositories = {}
		self.packages = {}

	@Step.error_checks
	def process(self):
		ok = True
		logger.info(self.log_path() + 'Delivering to directory ' + self.location)
		packages = [p for p in self.packages.values() if p.publish]
		for repo in [self.repositories[p.repo] for p in packages if p.to_retrieve]:
			if not repo.is_reachable():
				msg = self.log_path() + 'Repository ' + repo.name + ' --> unreachable for delivery'
				logger.error(msg)
				self.checker.errors.append([msg])
				ok = False
		if ok:
			for package in packages:
				if package.to_retrieve:
					package.deliver(self.location, self.repositories[package.repo])
				else:
					self._set_workspace()
					package.deliver(self.location, Step.WORKSPACE)
				logger.info(self.log_path() + 'Delivered package : ' + package.format_name())
		return ok
		
	
	
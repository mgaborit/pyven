import os

from pyven.exceptions.exception import PyvenException
from pyven.exceptions.repository_exception import RepositoryException

from pyven.steps.step import Step
from pyven.checkers.checker import Checker

from pyven.logging.logger import Logger
from pyven.reporting.listing_generator import ListingGenerator

class Deliver(Step):
	def __init__(self, verbose, location):
		super(Deliver, self).__init__(verbose)
		self.name = 'deliver'
		self.checker = Checker('Delivery')
		self.location = location

	@Step.error_checks
	def _process(self, project):
		ok = True
		Logger.get().info('Delivering to directory ' + self.location)
		packages = [p for p in project.packages.values() if p.publish]
		for repo in [project.repositories[p.repo] for p in packages if p.to_retrieve]:
			if not repo.is_reachable():
				msg = 'Repository ' + repo.name + ' --> unreachable for delivery'
				Logger.get().error(msg)
				self.checker.errors.append([msg])
				ok = False
		if ok:
			for package in packages:
				if package.to_retrieve:
					package.deliver(self.location, project.repositories[package.repo])
				else:
					package.deliver(self.location, Step.WORKSPACE)
				Logger.get().info('Delivered package : ' + package.format_name())
		return ok
		
	def generator(self):
		generators = []
		if self.status in Step.STATUS[1:]:
			generators.append(self.checker.generator())
		return ListingGenerator(title=self.name, properties={'Status' : self.status}, generators=generators)
	
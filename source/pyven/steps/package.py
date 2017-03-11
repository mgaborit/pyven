import os

from pyven.exceptions.exception import PyvenException
from pyven.exceptions.repository_exception import RepositoryException

from pyven.steps.step import Step
from pyven.steps.utils import retrieve
from pyven.checkers.checker import Checker

from pyven.logging.logger import Logger
from pyven.reporting.listing_generator import ListingGenerator

class PackageStep(Step):
	def __init__(self, verbose):
		super(PackageStep, self).__init__(verbose)
		self.name = 'package'
		self.checker = Checker('Packaging')

	@Step.error_checks
	def _process(self, project):
		ok = retrieve('artifact', project, project.artifacts, self.checker) and retrieve('package', project, project.packages, self.checker)
		if ok:
			for package in [p for p in project.packages.values() if not p.to_retrieve]:
				try:
					if not package.pack(Step.WORKSPACE):
						ok = False
				except PyvenException as e:
					self.checker.errors.append(e.args)
					for msg in e.args:
						Logger.get().error(msg)
					ok = False
		return ok
		
	def generator(self):
		generators = []
		if self.status in Step.STATUS[1]:
			generators.append(self.checker.generator())
		return ListingGenerator(title=self.name, properties={'Status' : self.status}, generators=generators)
	
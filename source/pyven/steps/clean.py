from pyven.exceptions.exception import PyvenException

from pyven.steps.step import Step
from pyven.checkers.checker import Checker

from pyven.logging.logger import Logger
from pyven.reporting.listing_generator import ListingGenerator

class Clean(Step):
	def __init__(self, verbose):
		super(Clean, self).__init__(verbose)
		self.name = 'clean'
		self.checker = Checker('Cleaning')

	@Step.error_checks
	def _process(self, project):
		ok = True
		for tool in project.builders:
			if not tool.clean(self.verbose):
				build_ok = False
		for tool in project.preprocessors:
			if not tool.clean(self.verbose):
				preprocess_ok = False
		return ok
	
	def generator(self):
		generators = []
		for project in Step.PROJECTS:
			for builder in project.builders:
				generators.append(builder.generator())
		if self.status in Step.STATUS[1:]:
			generators.append(self.checker.generator())
		return ListingGenerator(title=self.name, properties={'Status' : self.status}, generators=generators)
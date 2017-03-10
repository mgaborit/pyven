from pyven.exceptions.exception import PyvenException

from pyven.steps.step import Step
from pyven.checkers.checker import Checker

from pyven.logging.logger import Logger

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
	
	
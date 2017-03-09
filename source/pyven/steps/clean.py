import logging, time

from pyven.exceptions.exception import PyvenException

from pyven.steps.step import Step
from pyven.checkers.checker import Checker

logger = logging.getLogger('global')

class Clean(Step):
	def __init__(self, path, verbose):
		super(Clean, self).__init__(path, verbose)
		self.name = 'clean'
		self.checker = Checker('Cleaning')
		self.preprocessors = []
		self.builders = []

	@Step.error_checks
	def process(self):
		ok = True
		for tool in self.builders:
			if not tool.clean(self.verbose):
				build_ok = False
		for tool in self.preprocessors:
			if not tool.clean(self.verbose):
				preprocess_ok = False
		return ok
	
	
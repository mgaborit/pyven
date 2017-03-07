import logging, time

from pyven.exceptions.exception import PyvenException

from pyven.steps.step import Step
from pyven.checkers.checker import Checker

logger = logging.getLogger('global')

class Build(Step):
	def __init__(self, path, verbose, warning_as_error=False):
		super(Build, self).__init__(path, verbose)
		self.name = 'build'
		self.checker = Checker('Build')
		self.tools = []
		self.warning_as_error = warning_as_error

	@Step.error_checks
	def process(self):
		logger.info(self.log_path() + 'Starting ' + self.name)
		ok = True
		for tool in self.tools:
			tic = time.time()
			if not tool.process(self.verbose, self.warning_as_error):
				ok = False
			else:
				toc = time.time()
				logger.info(self.log_path() + 'Time for ' + tool.type + ':' + tool.name + ' : ' + str(round(toc - tic, 3)) + ' seconds')
		if not ok:
			logger.error(self.name + ' errors found')
		else:
			logger.info(self.log_path() + self.name + ' completed')
		return ok
	
	
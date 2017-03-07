import logging, time

from pyven.exceptions.exception import PyvenException

from pyven.steps.step import Step
from pyven.checkers.checker import Checker

logger = logging.getLogger('global')

class Preprocess(Step):
	def __init__(self, path, verbose):
		super(Preprocess, self).__init__(path, verbose)
		self.name = 'preprocess'
		self.checker = Checker('Preprocessing')
		self.tools = []

	@Step.error_checks
	def process(self):
		logger.info(self.log_path() + 'Starting ' + self.name)
		ok = True
		for tool in self.tools:
			tic = time.time()
			if not tool.process(self.verbose):
				ok = False
			else:
				toc = time.time()
				logger.info(self.log_path() + 'Time for ' + tool.type + ':' + tool.name + ' : ' + str(round(toc - tic, 3)) + ' seconds')
		if not ok:
			logger.error(self.name + ' errors found')
		else:
			logger.info(self.log_path() + self.name + ' completed')
		return ok
	
	
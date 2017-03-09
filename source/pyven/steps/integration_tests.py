import logging, time

from pyven.steps.step import Step
from pyven.checkers.checker import Checker

logger = logging.getLogger('global')

class IntegrationTests(Step):
	def __init__(self, path, verbose):
		super(IntegrationTests, self).__init__(path, verbose)
		self.name = 'verify'
		self.checker = Checker('Integration tests')
		self.tests = []

	@Step.error_checks
	def process(self):
		ok = True
		if len(self.tests) == 0:
			logger.warning(self.log_path() + 'No unit tests found')
		else:
			for test in self.tests:
				tic = time.time()
				if not test.process(self.verbose, Step.WORKSPACE):
					ok = False
				else:
					toc = time.time()
					logger.info(self.log_path() + 'Time for test ' + test.filename + ' : ' + str(round(toc - tic, 3)) + ' seconds')
		if not ok:
			logger.error('Integration tests failures found')
		return ok
	
	
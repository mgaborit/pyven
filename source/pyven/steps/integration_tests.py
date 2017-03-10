import time

from pyven.steps.step import Step
from pyven.checkers.checker import Checker

from pyven.logging.logger import Logger

class IntegrationTests(Step):
	def __init__(self, verbose):
		super(IntegrationTests, self).__init__(verbose)
		self.name = 'verify'
		self.checker = Checker('Integration tests')

	@Step.error_checks
	def _process(self, project):
		ok = True
		if len(project.integration_tests) == 0:
			Logger.get().warning('No unit tests found')
		else:
			for test in project.integration_tests:
				tic = time.time()
				if not test.process(self.verbose, Step.WORKSPACE):
					ok = False
				else:
					toc = time.time()
					Logger.get().info('Time for test ' + test.filename + ' : ' + str(round(toc - tic, 3)) + ' seconds')
		if not ok:
			Logger.get().error('Integration tests failures found')
		return ok
	
	
import time

from pyven.steps.step import Step
from pyven.checkers.checker import Checker

from pyven.logging.logger import Logger
from pyven.reporting.content.step import StepListing

class IntegrationTests(Step):
	def __init__(self, verbose):
		super(IntegrationTests, self).__init__(verbose)
		self.name = 'verify'
		self.checker = Checker('Integration tests')

	@Step.error_checks
	def _process(self, project):
		ok = True
		if len(project.integration_tests) == 0:
			Logger.get().warning('No integration tests configured')
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
	
	def content(self):
		listings = []
		for project in Step.PROJECTS:
			for test in project.integration_tests:
				listings.append(test.content())
		if self.status == Step.STATUS[1]:
			listings.append(self.checker.content())
		return StepListing(title=self.title(), status=self.report_status(), listings=listings)
		
	def report(self):
		report = super(IntegrationTests, self).report()
		if report:
			i = 0
			nb_tests = 0
			while nb_tests == 0 and i < len(Step.PROJECTS):
				nb_tests += len(Step.PROJECTS[i].integration_tests)
				i += 1
			report = nb_tests > 0
		return report
		
import time

from pyven.steps.step import Step
from pyven.checkers.checker import Checker

from pyven.logging.logger import Logger
from pyven.reporting.listing_generator import ListingGenerator

class UnitTests(Step):
	def __init__(self, verbose):
		super(UnitTests, self).__init__(verbose)
		self.name = 'test'
		self.checker = Checker('Unit tests')

	@Step.error_checks
	def _process(self, project):
		ok = True
		if len(project.unit_tests) == 0:
			Logger.get().warning('No unit tests configured')
		else:
			for test in project.unit_tests:
				tic = time.time()
				if not test.process(self.verbose):
					ok = False
				else:
					toc = time.time()
					Logger.get().info('Time for test ' + test.filename + ' : ' + str(round(toc - tic, 3)) + ' seconds')
		if not ok:
			Logger.get().error('Unit tests failures found')
		return ok
	
	def generator(self):
		generators = []
		for project in Step.PROJECTS:
			for test in project.unit_tests:
				generators.append(test.generator())
		if self.status in Step.STATUS[1]:
			generators.append(self.checker.generator())
		return ListingGenerator(title=self.name, properties={'Status' : self.status}, generators=generators)
		
	def report(self):
		report = super(UnitTests, self).report()
		if report:
			i = 0
			nb_tests = 0
			while nb_tests == 0 and i < len(Step.PROJECTS):
				nb_tests += len(Step.PROJECTS[i].unit_tests)
				i += 1
			report = nb_tests > 0
		return report
		
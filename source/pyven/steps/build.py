import time

from pyven.exceptions.exception import PyvenException

from pyven.steps.step import Step
from pyven.checkers.checker import Checker

from pyven.logging.logger import Logger
from pyven.reporting.listing_generator import ListingGenerator

class Build(Step):
	def __init__(self, verbose, warning_as_error=False):
		super(Build, self).__init__(verbose)
		self.name = 'build'
		self.checker = Checker('Build')
		self.warning_as_error = warning_as_error

	@Step.error_checks
	def _process(self, project):
		Logger.get().info('Starting ' + self.name)
		ok = True
		for tool in project.builders:
			tic = time.time()
			if not tool.process(self.verbose, self.warning_as_error):
				ok = False
			else:
				toc = time.time()
				Logger.get().info('Time for ' + tool.type + ':' + tool.name + ' : ' + str(round(toc - tic, 3)) + ' seconds')
		if not ok:
			Logger.get().error(self.name + ' errors found')
		else:
			Logger.get().info(self.name + ' completed')
		return ok
	
	def generator(self):
		generators = []
		for project in Step.PROJECTS:
			for builder in project.builders:
				generators.append(builder.generator())
		if self.status in Step.STATUS[1]:
			generators.append(self.checker.generator())
		return ListingGenerator(title=self.name, properties={'Status' : self.status}, generators=generators)
		
	def report(self):
		report = super(Build, self).report()
		if report:
			i = 0
			nb_builders = 0
			while nb_builders == 0 and i < len(Step.PROJECTS):
				nb_builders += len(Step.PROJECTS[i].builders)
				i += 1
			report = nb_builders > 0
		return report
		
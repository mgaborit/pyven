import time

from pyven.exceptions.exception import PyvenException

from pyven.steps.step import Step
from pyven.checkers.checker import Checker

from pyven.logging.logger import Logger
from pyven.reporting.content.step import StepListing

class Postprocess(Step):
	def __init__(self, verbose):
		super(Postprocess, self).__init__(verbose)
		self.name = 'postprocess'
		self.checker = Checker('Postprocessing')

	@Step.error_checks
	def _process(self, project):
		Logger.get().info('Starting ' + self.name)
		ok = True
		for tool in project.postprocessors:
			tic = time.time()
			if not tool.process(self.verbose):
				ok = False
			else:
				toc = time.time()
				Logger.get().info('Time for ' + tool.type + ':' + tool.name + ' : ' + str(round(toc - tic, 3)) + ' seconds')
		if not ok:
			Logger.get().error(self.name + ' errors found')
		else:
			Logger.get().info(self.name + ' completed')
		return ok
	
	def content(self):
		listings = []
		if self.status == Step.STATUS[1]:
			for project in Step.PROJECTS:
				for postprocessor in project.postprocessors:
					listings.append(postprocessor.content())
			if self.checker.enabled():
				listings.append(self.checker.content())
		return StepListing(title=self.title(), status=self.report_status(), listings=listings, enable_summary=True)
		
	def report(self):
		return self.status == Step.STATUS[1]
		
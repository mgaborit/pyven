import time

from pyven.exceptions.exception import PyvenException

from pyven.steps.step import Step
from pyven.checkers.checker import Checker

from pyven.logging.logger import Logger

class Preprocess(Step):
	def __init__(self, verbose):
		super(Preprocess, self).__init__(verbose)
		self.name = 'preprocess'
		self.checker = Checker('Preprocessing')

	@Step.error_checks
	def _process(self, project):
		Logger.get().info('Starting ' + self.name)
		ok = True
		for tool in project.preprocessors:
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
	
	
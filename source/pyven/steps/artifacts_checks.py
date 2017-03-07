import logging, time

from pyven.exceptions.exception import PyvenException

from pyven.steps.step import Step
from pyven.checkers.checker import Checker

logger = logging.getLogger('global')

class ArtifactsChecks(Step):
	def __init__(self, path, verbose):
		super(ArtifactsChecks, self).__init__(path, verbose)
		self.name = 'artifacts checks'
		self.checker = Checker('Artifacts')
		self.artifacts = {}

	@Step.error_checks
	def process(self):
		logger.info(self.log_path() + 'Starting ' + self.name)
		ok = True
		for artifact in [a for a in self.artifacts.values() if not a.to_retrieve]:
			if not artifact.check(self.checker):
				logger.error(self.log_path() + 'Artifact ' + artifact.format_name() + ' --> KO')
				ok = False
			else:
				logger.info(self.log_path() + 'Artifact ' + artifact.format_name() + ' --> OK')
		if ok:
			logger.error('Artifacts missing')
		else:
			logger.info(self.log_path() + self.name + ' completed')
		return ok
	
	
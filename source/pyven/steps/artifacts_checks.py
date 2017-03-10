from pyven.exceptions.exception import PyvenException

from pyven.steps.step import Step
from pyven.checkers.checker import Checker

from pyven.logging.logger import Logger
from pyven.reporting.listing_generator import ListingGenerator

class ArtifactsChecks(Step):
	def __init__(self, verbose):
		super(ArtifactsChecks, self).__init__(verbose)
		self.name = 'artifacts checks'
		self.checker = Checker('Artifacts')

	@Step.error_checks
	def _process(self, project):
		Logger.get().info('Starting ' + self.name)
		ok = True
		for artifact in [a for a in project.artifacts.values() if not a.to_retrieve]:
			if not artifact.check(self.checker):
				Logger.get().error('Artifact ' + artifact.format_name() + ' --> KO')
				ok = False
			else:
				Logger.get().info('Artifact ' + artifact.format_name() + ' --> OK')
		if not ok:
			Logger.get().error('Artifacts missing')
		else:
			for artifact in [a for a in project.artifacts.values() if not a.to_retrieve]:
				Step.WORKSPACE.publish(artifact, artifact.file)
			Logger.get().info(self.name + ' completed')
		return ok
	
	def generator(self):
		generators = []
		if self.status in Step.STATUS[1:]:
			generators.append(self.checker.generator())
		return ListingGenerator(title=self.name, properties={'Status' : self.status}, generators=generators)
import pyven.constants
from pyven.steps.step import Step
from pyven.checkers.checker import Checker

from pyven.logging.logger import Logger
from pyven.reporting.content.step import StepListing

class Install(Step):
    def __init__(self, verbose):
        super(Install, self).__init__(verbose)
        self.name = 'install'
        self.checker = Checker('Installation')

    def process(self):
        return self._process_sequential()
    
    @Step.error_checks
    def _process(self, project):
        ok = True
        for artifact in [a for a in project.artifacts.values() if a.publish]:
            Step.LOCAL_REPO.publish(artifact, Step.WORKSPACE)
            Logger.get().info('Repository ' + Step.LOCAL_REPO.name + ' --> Published artifact ' + artifact.format_name())
        for package in [p for p in project.packages.values() if p.publish]:
            Step.LOCAL_REPO.publish(package, Step.WORKSPACE)
            Logger.get().info('Repository ' + Step.LOCAL_REPO.name + ' --> Published package ' + package.format_name())
        if not ok:
            project.status = pyven.constants.STATUS[1]
            Logger.get().error(self.name + ' errors found')
        else:
            project.status = pyven.constants.STATUS[0]
            Logger.get().info(self.name + ' completed')
        return ok
        
    def report_content(self):
        listings = []
        if self.checker.enabled():
            listings.append(self.checker.report_content())
        return StepListing(title=self.title(), status=self.report_status(), listings=listings)
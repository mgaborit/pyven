import pyven.constants
from pyven.steps.step import Step
from pyven.checkers.checker import Checker

from pyven.logging.logger import Logger
from pyven.reporting.content.step import StepListing

class Clean(Step):
    def __init__(self, verbose, nb_threads=1):
        super(Clean, self).__init__(verbose)
        self.name = 'clean'
        self.checker = Checker('Cleaning')
        self.nb_threads = nb_threads

    def process(self):
        return self._process_parallel()
    
    @Step.error_checks
    def _process(self, project):
        ok = True
        for tool in project.builders:
            if not tool.clean(self.verbose):
                ok = False
        for tool in project.preprocessors:
            if not tool.clean(self.verbose):
                ok = False
        if not ok:
            project.status = pyven.constants.STATUS[1]
            Logger.get().error(self.name + ' errors found')
        else:
            project.status = pyven.constants.STATUS[0]
            Logger.get().info(self.name + ' completed')
        return ok
    
    def content(self):
        listings = []
        for project in Step.PROJECTS:
            for builder in project.builders:
                listings.append(builder.content())
        if self.checker.enabled():
            listings.append(self.checker.content())
        return StepListing(title=self.title(), status=self.report_status(), listings=listings, enable_summary=True)
        
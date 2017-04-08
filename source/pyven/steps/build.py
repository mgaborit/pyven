import time

import pyven.constants
from pyven.steps.step import Step
from pyven.checkers.checker import Checker

from pyven.logging.logger import Logger
from pyven.reporting.content.step import StepListing

class Build(Step):
    def __init__(self, verbose, warning_as_error=False, nb_threads=1):
        super(Build, self).__init__(verbose)
        self.name = 'build'
        self.checker = Checker('Build')
        self.warning_as_error = warning_as_error
        self.nb_threads = nb_threads

    def process(self):
        return self._process_parallel()
    
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
        
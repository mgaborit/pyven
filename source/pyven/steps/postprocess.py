import time

import pyven.constants
from pyven.steps.step import Step
from pyven.checkers.checker import Checker

from pyven.logging.logger import Logger
from pyven.reporting.content.step import StepListing

class Postprocess(Step):
    def __init__(self, verbose, nb_threads=1):
        super(Postprocess, self).__init__(verbose)
        self.name = 'postprocess'
        self.checker = Checker('Postprocessing')
        self.nb_threads = nb_threads

    def process(self):
        return self._process_parallel()
    
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
            project.status = pyven.constants.STATUS[1]
            Logger.get().error(self.name + ' errors found')
        else:
            project.status = pyven.constants.STATUS[0]
            Logger.get().info(self.name + ' completed')
        return ok
    
    def report_content(self):
        listings = []
        if self.status == pyven.constants.STATUS[1]:
            for project in Step.PROJECTS:
                for postprocessor in project.postprocessors:
                    listings.append(postprocessor.report_content())
            if self.checker.enabled():
                listings.append(self.checker.report_content())
        return StepListing(title=self.title(), status=self.report_status(), listings=listings, enable_summary=True)
        
    def report(self):
        return self.status == pyven.constants.STATUS[1]
        
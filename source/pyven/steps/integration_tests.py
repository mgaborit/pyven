from threading import Thread

import pyven.constants
from pyven.steps.step import Step
from pyven.checkers.checker import Checker

from pyven.logging.logger import Logger
from pyven.reporting.content.step import StepListing

from pyven.utils.parallelizer import Parallelizer

class IntegrationTests(Step):
    def __init__(self, verbose, nb_threads=1):
        super(IntegrationTests, self).__init__(verbose)
        self.name = 'verify'
        self.checker = Checker('Integration tests')
        self.nb_threads = nb_threads
        self.parallelizer = Parallelizer(max_concurrent=self.nb_threads)

    def process(self):
        self.parallelizer.threads = []
        if self._process_sequential():
            self.parallelizer.run()
        ok = True
        for project in Step.PROJECTS:
            for test in project.unit_tests:
                if test.status in pyven.constants.STATUS[1:]:
                    ok = False
        if not ok:
            self.status = Step.STATUS[1]
            Logger.get().error(self.name + ' errors found')
        else:
            self.status = Step.STATUS[0]
            Logger.get().info(self.name + ' completed')
        return ok
    
    @Step.error_checks
    def _process(self, project):
        if len(project.integration_tests) == 0:
            Logger.get().warning('No integration tests configured')
        else:
            for test in project.integration_tests:
                self.parallelizer.threads.append(Thread(target=test.process, args=(self.verbose, Step.WORKSPACE)))
        return True
    
    def content(self):
        listings = []
        for project in Step.PROJECTS:
            for test in project.integration_tests:
                listings.append(test.content())
        if self.checker.enabled():
            listings.append(self.checker.content())
        return StepListing(title=self.title(), status=self.report_status(), listings=listings, enable_summary=True)
        
    def report(self):
        report = super(IntegrationTests, self).report()
        if report:
            i = 0
            nb_tests = 0
            while nb_tests == 0 and i < len(Step.PROJECTS):
                nb_tests += len(Step.PROJECTS[i].integration_tests)
                i += 1
            report = nb_tests > 0
        return report
        
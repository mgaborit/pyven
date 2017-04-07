from pyven.exceptions.exception import PyvenException

from pyven.steps.step import Step
from pyven.steps.utils import retrieve
from pyven.checkers.checker import Checker

from pyven.logging.logger import Logger
from pyven.reporting.content.step import StepListing

class PackageStep(Step):
    def __init__(self, verbose, nb_threads=1):
        super(PackageStep, self).__init__(verbose)
        self.name = 'package'
        self.checker = Checker('Packaging')
        self.nb_threads = nb_threads

    def process(self):
        return self._process_parallel()
    
    @Step.error_checks
    def _process(self, project):
        ok = retrieve('artifact', project, project.artifacts, self.checker) and retrieve('package', project, project.packages, self.checker)
        if ok:
            for package in [p for p in project.packages.values() if not p.to_retrieve]:
                try:
                    if not package.pack(Step.WORKSPACE):
                        ok = False
                except PyvenException as e:
                    self.checker.errors.append(e.args)
                    for msg in e.args:
                        Logger.get().error(msg)
                    ok = False
        if not ok:
            self.status = Step.STATUS[1]
            Logger.get().error(self.name + ' errors found')
        else:
            self.status = Step.STATUS[0]
            Logger.get().info(self.name + ' completed')
        return ok
        
    def content(self):
        listings = []
        if self.checker.enabled():
            listings.append(self.checker.content())
        return StepListing(title=self.title(), status=self.report_status(), listings=listings)
    
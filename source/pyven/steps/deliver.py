import pyven.constants
from pyven.steps.step import Step
from pyven.checkers.checker import Checker

from pyven.logging.logger import Logger
from pyven.reporting.content.step import StepListing

class Deliver(Step):
    def __init__(self, verbose, location):
        super(Deliver, self).__init__(verbose)
        self.name = 'deliver'
        self.checker = Checker('Delivery')
        self.location = location

    def process(self):
        return self._process_sequential()
    
    @Step.error_checks
    def _process(self, project):
        ok = True
        Logger.get().info('Delivering to directory ' + self.location)
        packages = [p for p in project.packages.values()]
        for repo in [project.repositories[p.repo] for p in packages if p.to_retrieve]:
            if not repo.is_reachable():
                msg = 'Repository ' + repo.name + ' --> unreachable for delivery'
                Logger.get().error(msg)
                self.checker.errors.append([msg])
                ok = False
        if ok:
            for package in packages:
                if package.to_retrieve:
                    package.deliver(self.location, project.repositories[package.repo])
                else:
                    package.deliver(self.location, Step.WORKSPACE)
                Logger.get().info('Delivered package : ' + package.format_name())
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
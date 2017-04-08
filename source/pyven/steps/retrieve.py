import os, shutil

import pyven.constants
from pyven.steps.step import Step
from pyven.steps.utils import retrieve
from pyven.checkers.checker import Checker

from pyven.logging.logger import Logger
from pyven.reporting.content.step import StepListing

class Retrieve(Step):
    def __init__(self, verbose):
        super(Retrieve, self).__init__(verbose)
        self.name = 'retrieve'
        self.checker = Checker('Retrieval')

    def process(self):
        return self._process_sequential()
    
    @Step.error_checks
    def _process(self, project):
        ok = retrieve('artifact', project, project.artifacts, self.checker) and retrieve('package', project, project.packages, self.checker)
        if ok:
            for package in [p for p in project.packages.values() if not p.to_retrieve]:
                for item in [i for i in package.items if i.to_retrieve]:
                    for built_item in [i for i in package.items if not i.to_retrieve]:
                        dir = os.path.dirname(built_item.file)
                        if not os.path.isdir(dir):
                            os.makedirs(dir)
                        Logger.get().info('Copying artifact ' + item.format_name() + ' to directory ' + dir)
                        shutil.copy(os.path.join(item.location(Step.WORKSPACE.url), item.basename()), os.path.join(dir, item.basename()))
        if not ok:
            project.status = pyven.constants.STATUS[1]
            Logger.get().error(self.name + ' errors found')
        else:
            project.status = pyven.constants.STATUS[0]
            Logger.get().info(self.name + ' completed')
        return ok
        
    def content(self):
        listings = []
        if self.checker.enabled():
            listings.append(self.checker.content())
        return StepListing(title=self.title(), status=self.report_status(), listings=listings)
    
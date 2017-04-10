import pyven.constants
from pyven.exceptions.repository_exception import RepositoryException

from pyven.steps.step import Step
from pyven.checkers.checker import Checker

from pyven.logging.logger import Logger
from pyven.reporting.content.step import StepListing

class Deploy(Step):
    def __init__(self, verbose, release):
        super(Deploy, self).__init__(verbose)
        self.name = 'deploy'
        self.checker = Checker('Deployment')
        self.release = release

    def process(self):
        return self._process_sequential()
    
    @Step.error_checks
    def _process(self, project):
        ok = True
        repositories = [r for r in project.repositories.values() if (not r.release or (r.release and self.release))\
                                                                    and r.name != Step.WORKSPACE.name\
                                                                    and r.name != Step.LOCAL_REPO.name]
        for repo in repositories:
            if not repo.is_reachable():
                msg = 'Repository ' + repo.name + ' --> unreachable for deployment'
                Logger.get().error(msg)
                self.checker.errors.append([msg])
                ok = False
        if ok:
            for repo in repositories:
                try:
                    for artifact in [a for a in project.artifacts.values() if a.publish]:
                        repo.publish(artifact, Step.WORKSPACE)
                        Logger.get().info('Repository ' + repo.name + ' --> Published artifact ' + artifact.format_name())
                    for package in [p for p in project.packages.values() if p.publish]:
                        repo.publish(package, Step.WORKSPACE)
                        Logger.get().info('Repository ' + repo.name + ' --> Published package ' + package.format_name())
                except RepositoryException as e:
                    self.checker.errors.append(e.args)
                    for msg in e.args:
                        Logger.get().error(msg)
                    raise e
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
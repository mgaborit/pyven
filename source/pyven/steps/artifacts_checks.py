import pyven.constants
from pyven.steps.step import Step
from pyven.checkers.checker import Checker

from pyven.logging.logger import Logger
from pyven.reporting.content.step import StepListing

class ArtifactsChecks(Step):
    def __init__(self, verbose, nb_threads=1):
        super(ArtifactsChecks, self).__init__(verbose)
        self.name = 'artifacts checks'
        self.checker = Checker('Artifacts')
        self.nb_threads = nb_threads

    def process(self):
        return self._process_parallel()
    
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
            project.status = pyven.constants.STATUS[1]
            Logger.get().error('Artifacts missing')
        else:
            for artifact in [a for a in project.artifacts.values() if not a.to_retrieve]:
                Step.WORKSPACE.publish(artifact, artifact.file)
            project.status = pyven.constants.STATUS[0]
            Logger.get().info(self.name + ' completed')
        return ok
    
    def content(self):
        listings = []
        if self.status in pyven.constants.STATUS[1]:
            listings.append(self.checker.content())
        return StepListing(title=self.title(), status=self.report_status(), listings=listings)
        
    def report(self):
        report = super(ArtifactsChecks, self).report()
        if report:
            i = 0
            nb_artifacts = 0
            while nb_artifacts == 0 and i < len(Step.PROJECTS):
                nb_artifacts += len([a for a in Step.PROJECTS[i].artifacts.values() if not a.to_retrieve])
                i += 1
            report = nb_artifacts > 0
        return report
        
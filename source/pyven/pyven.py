import os

import pyven.constants
from pyven.logging.logger import Logger

from pyven.reporting.html_utils import HTMLUtils
from pyven.utils.pym_writer import PymWriter

from pyven.repositories.directory import DirectoryRepo
from pyven.repositories.workspace import Workspace

from pyven.reporting.content.platform import Platform
from pyven.reporting.content.success import Success
from pyven.reporting.content.failure import Failure
from pyven.reporting.content.unknown import Unknown
from pyven.reporting.content.title import Title
from pyven.reporting.content.lines import Lines

from pyven.steps.step import Step
from pyven.steps.configure import Configure
from pyven.steps.preprocess import Preprocess
from pyven.steps.build import Build
from pyven.steps.postprocess import Postprocess
from pyven.steps.artifacts_checks import ArtifactsChecks
from pyven.steps.unit_tests import UnitTests
from pyven.steps.package import PackageStep
from pyven.steps.integration_tests import IntegrationTests
from pyven.steps.install import Install
from pyven.steps.deploy import Deploy
from pyven.steps.retrieve import Retrieve
from pyven.steps.deliver import Deliver
from pyven.steps.clean import Clean

class Pyven:    
    WORKSPACE = Workspace('workspace', 'workspace', os.path.join(os.getcwd(), 'pvn_workspace'))
    if not os.path.isdir(WORKSPACE.url):
        os.makedirs(WORKSPACE.url)
    Logger.get().info('Workspace set at : ' + WORKSPACE.url)

    if pyven.constants.PLATFORM == 'windows':
        LOCAL_REPO = DirectoryRepo('local', 'file', os.path.join(os.environ.get('USERPROFILE'), 'pvn_repo'))
    elif pyven.constants.PLATFORM == 'linux':
        LOCAL_REPO = DirectoryRepo('local', 'file', os.path.join(os.environ.get('HOME'), 'pvn_repo'))
    if not os.path.isdir(LOCAL_REPO.url):
        os.makedirs(LOCAL_REPO.url)

    Step.WORKSPACE = WORKSPACE
    Step.LOCAL_REPO = LOCAL_REPO

    STEPS = ['deliver', 'clean', 'retrieve', 'configure', 'preprocess', 'build', 'test', 'package', 'verify', 'install', 'deploy']
    UTILS = ['init', 'aggregate']
    
    def __init__(self, step, verbose=False, warning_as_error=False, pym='pym.xml', release=False, overwrite=False, path='', arguments={}, nb_lines=10, nb_threads=1):
        self.pym = pym
        self.path = path
        self.arguments = arguments
        self.step = step
        self.verbose = verbose
        self.nb_lines = nb_lines
        self.nb_threads = nb_threads
        Logger.get().info('Number of threads : ' + str(self.nb_threads))
        self.status = pyven.constants.STATUS[2]
        if self.verbose:
            Logger.get().info('Verbose mode enabled')
        self.release = release
        if self.release:
            Logger.get().info('Release mode enabled')
        self.overwrite = overwrite
        if self.overwrite:
            Logger.get().info('Release artifacts and packages will be overwritten')
        self.warning_as_error = warning_as_error
        if self.warning_as_error:
            Logger.get().info('Warnings will be considered as errors')

        self.configure = None
        self.steps = []
        if step in Pyven.STEPS:
            self.configure = Configure(self.verbose, self.pym)
            self.steps.append(self.configure)
            step_id = Pyven.STEPS.index(step)
            if step_id > Pyven.STEPS.index('configure'):
                self.steps.append(Preprocess(self.verbose, self.nb_threads))
                
            if step_id > Pyven.STEPS.index('preprocess'):
                self.steps.append(Build(self.verbose, self.warning_as_error, self.nb_threads))
                self.steps.append(Postprocess(self.verbose, self.nb_threads))
                self.steps.append(ArtifactsChecks(self.verbose, self.nb_threads))
                
            if step_id > Pyven.STEPS.index('build'):
                self.steps.append(UnitTests(self.verbose, self.nb_threads))
            
            if step_id > Pyven.STEPS.index('test'):
                self.steps.append(PackageStep(self.verbose))
            
            if step_id > Pyven.STEPS.index('package'):
                self.steps.append(IntegrationTests(self.verbose, self.nb_threads))
            
            if step_id > Pyven.STEPS.index('verify'):
                if step_id > Pyven.STEPS.index('install'):
                    self.steps.append(Deploy(self.verbose, self.release, self.overwrite))
            
                else:
                    self.steps.append(Install(self.verbose))
            
            
            elif step_id < Pyven.STEPS.index('configure'):
                if step_id == Pyven.STEPS.index('deliver'):
                    self.steps.append(Deliver(self.verbose, arguments['path']))
                    
                elif step_id == Pyven.STEPS.index('clean'):
                    self.steps.append(Clean(self.verbose, self.nb_threads))
                
                elif step_id == Pyven.STEPS.index('retrieve'):
                    self.steps.append(Retrieve(self.verbose))                     
                
    def process(self):
        ok = True
        i = 0
        self.status = pyven.constants.STATUS[0]
        while ok and i < len(self.steps):
            if not self.steps[i].process():
                ok = False
                self.status = pyven.constants.STATUS[1]
            i += 1
        return ok
        
    def aggregate(function):
        def _intern(self, report_style):
            if self.step in Pyven.STEPS[Pyven.STEPS.index('configure'):]:
                HTMLUtils.clean(Step.WORKSPACE.url)
            function(self, report_style)
            HTMLUtils.aggregate(Step.WORKSPACE.url)
        return _intern
    
    @aggregate
    def report(self, report_style):
        HTMLUtils.set_style(report_style)
        Lines.NB_LINES = self.nb_lines
        listings = []
        for step in self.steps:
            if step.report():
                listings.append(step.report_content())
        status = None
        if self.status == pyven.constants.STATUS[0]:
            status = Success()
        elif self.status == pyven.constants.STATUS[1]:
            status = Failure()
        else:
            status = Unknown()
        title = ''
        if self.configure is not None:
            title = self.configure.project_title()
            if title != '':
                title += ' - '
        content = Platform(title=Title(title + pyven.constants.PLATFORM), status=status, listings=listings)
        HTMLUtils.write(content.write(), Step.WORKSPACE.url, self.step)
        
    def display(self):
        HTMLUtils.display(Step.WORKSPACE.url)
    
    def init(self):
        PymWriter.write()
        return True
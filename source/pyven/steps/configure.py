import os

import pyven.constants
from pyven.steps.step import Step
from pyven.checkers.checker import Checker
from pyven.parser.pym_parser import PymParser
from pyven.parser.constants_parser import ConstantsParser
from pyven.exceptions.exception import PyvenException
from pyven.project import Project

from pyven.logging.logger import Logger
from pyven.reporting.content.step import StepListing

class Configure(Step):
    def __init__(self, verbose, pym):
        super(Configure, self).__init__(verbose)
        self.pym = pym
        self.name = 'configure'
        self.checker = Checker('Configuration')
        self.parsers = []

    def project_title(self):
        return self.parsers[0].parse_project_title()
        
    def report_content(self):
        listings = []
        if self.checker.enabled():
            listings.append(self.checker.report_content())
        return StepListing(title=self.title(), status=self.report_status(), listings=listings)
        
    def report(self):
        return self.status == pyven.constants.STATUS[1]
       
    @Step.step
    def process(self):
        project = Project(os.getcwd())
        cst_file = os.path.join(os.getcwd(), 'const.xml')
        if os.path.isfile(cst_file):
            cst_tree = PymParser.parse_xml(cst_file)
            project.constants = ConstantsParser('/constants/constant', os.getcwd()).parse(cst_tree)
        return self._process(project)
     
    @Step.error_checks
    def _process(self, project):
        parser = PymParser(os.path.join(project.path, self.pym), project.plugins)
        self.parsers.append(parser)
        parser.parse_pym()
        parser.parse_plugins()
        for k, v in parser.parse_constants().items():
            project.constants[k] = v
        ok = self._configure_projects(project, parser)\
            and self._configure_repositories(project, parser)\
            and self._configure_artifacts(project, parser)\
            and self._configure_packages(project, parser)\
            and self._configure_processes(project, parser)
        if ok:
            Step.PROJECTS.append(project)
        return ok
    
    def _configure_error_checks(function):
        def __intern(self, project, parser):
            ok = True
            try:
                function(self, project, parser)
            except PyvenException as e:
                self.checker.errors.append(e.args)
                for msg in e.args:
                    Logger.get().error(msg)
                ok = False
            return ok
        return __intern
        
    @_configure_error_checks
    def _configure_projects(self, project, parser):
        directories = parser.parse_projects()
        for directory in directories:
            if not os.path.isdir(os.path.join(project.path, directory)):
                raise PyvenException('Subproject directory does not exist : ' + directory)
            else:
                full_path = os.path.join(project.path, directory)
                subproject = Project(full_path, parser.plugins_manager.plugins.copy())
                subproject.constants = project.constants.copy()
                if not self._process(subproject):
                  raise PyvenException('Subproject ' + full_path + ' --> configuration failed')
                Logger.get().info('Added subproject --> ' + directory)
    
    @_configure_error_checks
    def _configure_repositories(self, project, parser):
        repositories = parser.parse_repositories()
        project.repositories[Step.WORKSPACE.name] = Step.WORKSPACE
        project.repositories[Step.LOCAL_REPO.name] = Step.LOCAL_REPO
        for repo in repositories:
            if repo.name == 'workspace' or repo.name == Step.LOCAL_REPO.name:
                raise PyvenException('Repository name reserved --> ' + repo.name + ' : ' + repo.url)
            else:
                if repo.name in project.repositories.keys():
                    raise PyvenException('Repository already added --> ' + repo.name + ' : ' + repo.url)
                else:
                    project.repositories[repo.name] = repo
                    if repo.is_reachable():
                        if repo.release:
                            Logger.get().info('Release repository added --> ' + repo.name + ' : ' + repo.url)
                        else:
                            Logger.get().info('Repository added --> ' + repo.name + ' : ' + repo.url)
                    else:
                        Logger.get().warning('Repository not accessible --> ' + repo.name + ' : ' + repo.url)
        
    @_configure_error_checks
    def _configure_artifacts(self, project, parser):
        artifacts = parser.parse_artifacts()
        for artifact in artifacts:
            artifact.company = project.replace_constants(artifact.company)
            artifact.name = project.replace_constants(artifact.name)
            artifact.config = project.replace_constants(artifact.config)
            artifact.version = project.replace_constants(artifact.version)
            if not artifact.to_retrieve:
                artifact.file = project.replace_constants(artifact.file)
            if artifact.format_name() in project.artifacts.keys():
                raise PyvenException('Artifact already added --> ' + artifact.format_name())
            elif artifact.to_retrieve and artifact.repo not in project.repositories.keys() and artifact.repo not in [Step.LOCAL_REPO.name, 'workspace']:
                raise PyvenException('Artifact repository not declared --> ' + artifact.format_name() + ' : repo ' + artifact.repo)
            else:
                project.artifacts[artifact.format_name()] = artifact
                Logger.get().info('Artifact added --> ' + artifact.format_name())
                if not artifact.publish:
                    Logger.get().info('Artifact ' + artifact.format_name() + ' --> publishment disabled')
        
    @_configure_error_checks
    def _configure_packages(self, project, parser):
        packages = parser.parse_packages()
        for package in packages:
            package.company = project.replace_constants(package.company)
            package.name = project.replace_constants(package.name)
            package.config = project.replace_constants(package.config)
            package.version = project.replace_constants(package.version)
            if len(package.deliveries) > 0:
                for i in range(len(package.deliveries)):
                    package.deliveries[i] = project.replace_constants(package.deliveries[i])
            items = []
            items.extend(package.items)
            package.items = []
            if package.format_name() in project.packages.keys():
                raise PyvenException('Package already added --> ' + package.format_name())
            elif package.to_retrieve and package.repo not in project.repositories.keys() and package.repo not in [Step.LOCAL_REPO.name, 'workspace']:
                raise PyvenException('Package repository not declared --> ' + package.format_name() + ' : repo ' + package.repo)
            else:
                for item in items:
                    item = project.replace_constants(item)
                    if item not in project.artifacts.keys():
                        raise PyvenException('Package ' + package.format_name() + ' : Artifact not declared --> ' + item)
                    else:
                        package.items.append(project.artifacts[item])
                        Logger.get().info('Package ' + package.format_name() + ' : Artifact added --> ' + item)
                project.packages[package.format_name()] = package
                Logger.get().info('Package added --> ' + package.format_name())
                if not package.publish:
                    Logger.get().info('Package ' + package.format_name() + ' --> publishment disabled')
        for package in packages:
            for extension in package.extensions:
                extension = project.replace_constants(extension)
                if extension not in project.packages.keys():
                    raise PyvenException('Package ' + package.format_name() + ' : Package extension not declared --> ' + extension)
                elif project.packages[extension].to_retrieve:
                    raise PyvenException('Package ' + package.format_name() + ' : Cannot extend a package to be retrieved --> ' + extension)
                else:
                    package.items.extend(project.packages[extension].items)
                    Logger.get().info('Package ' + package.format_name() + ' : Package extension added --> ' + extension)
                
    @_configure_error_checks
    def _configure_processes(self, project, parser):
        preprocessors = parser.parse_processes('preprocess', 'build/tools/tool', project)
        builders = parser.parse_processes('build', 'build/tools/tool', project)
        postprocessors = parser.parse_processes('postprocess', 'build/tools/tool', project)
        unit_tests = parser.parse_processes('test', 'tests/test', project)
        integration_tests = parser.parse_processes('verify', 'tests/test', project)
        
        project.preprocessors = self._check_processes('preprocessor', preprocessors, project)
        project.builders = self._check_processes('builder', builders, project)
        project.postprocessors = self._check_processes('postprocessor', postprocessors, project)
        project.unit_tests = self._check_processes('unit test', unit_tests, project)
        project.integration_tests = self._check_processes('integration test', integration_tests, project)
        
    def _check_processes(self, type, processes, project):
        for process in processes:
            process.name = project.replace_constants(process.name)
            Logger.get().info(type + ' added --> ' + process.type + ':' + process.name)
        return processes
        
        
        
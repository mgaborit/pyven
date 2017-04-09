import os

import pyven.constants
from pyven.steps.step import Step
from pyven.checkers.checker import Checker
from pyven.parser.pym_parser import PymParser
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
        return self._process(Project(os.getcwd()))
     
    @Step.error_checks
    def _process(self, project):
        parser = PymParser(os.path.join(project.path, self.pym))
        self.parsers.append(parser)
        parser.parse_pym()
        parser.parse_plugins()
        for k, v in parser.parse_constants().items():
            project.constants[k] = v
        ok = self._configure_projects(project, parser)\
            and self._configure_repositories(project, parser)\
            and self._configure_artifacts(project, parser)\
            and self._configure_packages(project, parser)\
            and self._configure_preprocessors(project, parser)\
            and self._configure_builders(project, parser)\
            and self._configure_postprocessors(project, parser)\
            and self._configure_unit_tests(project, parser)\
            and self._configure_valgrind_tests(project, parser)\
            and self._configure_integration_tests(project, parser)
        if ok:
            Step.PROJECTS.append(project)
        return ok
    
    @staticmethod
    def _replace_constants(str, constants):
        for name, value in constants.items():
            str = str.replace('$('+name+')', value)
        return str

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
                subproject = Project(full_path)
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
            artifact.company = Configure._replace_constants(artifact.company, project.constants)
            artifact.name = Configure._replace_constants(artifact.name, project.constants)
            artifact.config = Configure._replace_constants(artifact.config, project.constants)
            artifact.version = Configure._replace_constants(artifact.version, project.constants)
            if not artifact.to_retrieve:
                artifact.file = Configure._replace_constants(artifact.file, project.constants)
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
            package.company = Configure._replace_constants(package.company, project.constants)
            package.name = Configure._replace_constants(package.name, project.constants)
            package.config = Configure._replace_constants(package.config, project.constants)
            package.version = Configure._replace_constants(package.version, project.constants)
            package.delivery = Configure._replace_constants(package.delivery, project.constants)
            items = []
            items.extend(package.items)
            package.items = []
            if package.format_name() in project.packages.keys():
                raise PyvenException('Package already added --> ' + package.format_name())
            elif package.to_retrieve and package.repo not in project.repositories.keys() and package.repo not in [Step.LOCAL_REPO.name, 'workspace']:
                raise PyvenException('Package repository not declared --> ' + package.format_name() + ' : repo ' + package.repo)
            else:
                for item in items:
                    item = Configure._replace_constants(item, project.constants)
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
                extension = Configure._replace_constants(extension, project.constants)
                if extension not in project.packages.keys():
                    raise PyvenException('Package ' + package.format_name() + ' : Package extension not declared --> ' + extension)
                elif project.packages[extension].to_retrieve:
                    raise PyvenException('Package ' + package.format_name() + ' : Cannot extend a package to be retrieved --> ' + extension)
                else:
                    package.items.extend(project.packages[extension].items)
                    Logger.get().info('Package ' + package.format_name() + ' : Package extension added --> ' + extension)
                
        
    @_configure_error_checks
    def _configure_preprocessors(self, project, parser):
        preprocessors = parser.parse_preprocessors()
        checked = []
        for preprocessor in preprocessors:
            preprocessor.name = Configure._replace_constants(preprocessor.name, project.constants)
            checked.append(preprocessor)
            Logger.get().info('Pre-processor added --> ' + preprocessor.type + ':' + preprocessor.name)
        project.preprocessors = checked
        
    @_configure_error_checks
    def _configure_builders(self, project, parser):
        builders = parser.parse_builders()
        checked = []
        for builder in builders:
            builder.name = Configure._replace_constants(builder.name, project.constants)
            checked.append(builder)
            Logger.get().info('Builder added --> ' + builder.type + ':' + builder.name)
        project.builders = checked
        
    @_configure_error_checks
    def _configure_postprocessors(self, project, parser):
        postprocessors = parser.parse_postprocessors()
        checked = []
        for postprocessor in postprocessors:
            postprocessor.name = Configure._replace_constants(postprocessor.name, project.constants)
            checked.append(postprocessor)
            Logger.get().info('Post-processor added --> ' + postprocessor.type + ':' + postprocessor.name)
        project.postprocessors = checked
        
    @_configure_error_checks
    def _configure_unit_tests(self, project, parser):
        unit_tests = parser.parse_unit_tests()
        checked = []
        for unit_test in unit_tests:
            checked.append(unit_test)
            Logger.get().info('Unit test added --> ' + os.path.join(unit_test.path, unit_test.filename))
        project.unit_tests = checked
        
    @_configure_error_checks
    def _configure_valgrind_tests(self, project, parser):
        valgrind_tests = parser.parse_valgrind_tests()
        checked = []
        for valgrind_test in valgrind_tests:
            checked.append(valgrind_test)
            Logger.get().info('Valgrind test added --> ' + os.path.join(valgrind_test.path, valgrind_test.filename))
        self.valgrind_tests = checked
        
    @_configure_error_checks
    def _configure_integration_tests(self, project, parser):
        integration_tests = parser.parse_integration_tests()
        checked = []
        for integration_test in integration_tests:
            integration_test.package = Configure._replace_constants(integration_test.package, project.constants)
            if integration_test.package not in project.packages.keys():
                raise PyvenException('Integration test ' + os.path.join(integration_test.path, integration_test.filename)\
                            + ' : Package not declared --> ' + integration_test.package)
            else:
                integration_test.package = project.packages[integration_test.package]
                Logger.get().info('Integration test ' + os.path.join(integration_test.path, integration_test.filename)\
                            + ' : Package added --> ' + integration_test.package.format_name())
            checked.append(integration_test)
            Logger.get().info('Integration test added --> ' + os.path.join(integration_test.path, integration_test.filename))
        project.integration_tests = checked
        
        
        
        
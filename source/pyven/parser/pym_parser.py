import os
from pyven.logging.logger import Logger

import pyven.constants

from pyven.exceptions.parser_exception import ParserException

from pyven.checkers.checker import Checker
from pyven.plugins.manager import PluginsManager

from pyven.parser.constants_parser import ConstantsParser
from pyven.parser.directory_repo_parser import DirectoryRepoParser
from pyven.parser.artifacts_parser import ArtifactsParser
from pyven.parser.packages_parser import PackagesParser

from pyven.utils.utils import parse_xml

class PymParser(object):
    
    def __init__(self, pym='pym.xml', plugins={}):
        self.pym = pym
        self.plugins_manager = PluginsManager(plugins)
        self.repo_config = 'repositories.xml'
        self.plugins_config = 'plugins.xml'
        self.tree = None
        self.checker = Checker('Parser')
        self.constants_parser = ConstantsParser(os.path.dirname(self.pym))
        self.directory_repo_parser = DirectoryRepoParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/repositories/repository', os.path.dirname(self.pym))
        self.artifacts_parser = ArtifactsParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/artifacts/artifact', os.path.dirname(self.pym))
        self.packages_parser = PackagesParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/packages/package', os.path.dirname(self.pym))
    
    @staticmethod
    def check_version(tree, file):
        doc_element = tree.getroot()
        if doc_element is None or doc_element.tag == "name":
            raise ParserException('[' + file + '] Missing "pyven" tag')
        expected_pyven_version = doc_element.get('version')
        if expected_pyven_version is None:
            raise ParserException('[' + file + '] Missing Pyven version information')
        expected_pyven_version = expected_pyven_version.split('.')
        if len(expected_pyven_version) != 3:
            raise ParserException('[' + file + '] ill-formed pyven version --> Expected "MAJOR.MINOR.PATCH" but ' + '.'.join(expected_pyven_version) + ' found')
        if int(expected_pyven_version[0]) != pyven.constants.MAJOR:
            raise ParserException('[' + file + '] Invalid Pyven version --> MAJOR version number must be equal, expected : ' + '.'.join(expected_pyven_version) + ', actual : ' + pyven.constants.VERSION)
        if int(expected_pyven_version[1]) > pyven.constants.MINOR:
            raise ParserException('[' + file + '] Invalid Pyven version --> MINOR version number must be equal or greater, expected : ' + '.'.join(expected_pyven_version) + ', actual : ' + pyven.constants.VERSION)
        if int(expected_pyven_version[2]) > pyven.constants.PATCH:
            raise ParserException('[' + file + '] Invalid Pyven version --> PATCH version number must be equal or greater, expected : ' + '.'.join(expected_pyven_version) + ', actual : ' + pyven.constants.VERSION)
       
    def check_errors(function):
        def _intern(self, project=None):
            try:
                return function(self, project)
            except ParserException as e:
                self.checker.errors.append(e.args)
                raise e
        return _intern
    
    def check_errors_processes(function):
        def _intern(self, scope, xpath, project=None):
            try:
                return function(self, scope, xpath, project)
            except ParserException as e:
                self.checker.errors.append(e.args)
                raise e
        return _intern
    
    @check_errors
    def parse_pym(self, project=None):
        Logger.get().info('Starting ' + self.pym + ' parsing')
        self.tree = parse_xml(self.pym)
        PymParser.check_version(self.tree, self.pym)
        return True
        
    @check_errors
    def parse_plugins(self, project=None):
        repo_config = os.path.join(os.environ.get('PVN_HOME'), self.plugins_config)
        tree = parse_xml(repo_config)
        PymParser.check_version(tree, repo_config)
        if tree is not None:
            for plugin in tree.xpath('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/plugins/plugin'):
                name = plugin.get('name')
                version = plugin.get('version')
                if name is None:
                    raise ParserException('Missing plugin name')
                if version is None:
                    raise ParserException('Missing plugin version : ' + name)
                self.plugins_manager.plugins[name] = version
                Logger.get().info('Plugin ' + name + '_' + version + ' added')
        self.plugins_manager.load()
                
    @check_errors
    def parse_project_title(self, project=None):
        title = ''
        if self.tree is not None:
            nodes = self.tree.xpath('/pyven/project')
            if len(nodes) > 0:
                title += nodes[0].text
        return title
        
    @check_errors
    def parse_constants(self, project=None):
        return self.constants_parser.parse(self.tree)
        
    @check_errors
    def parse_projects(self, project=None):
        query = '/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/subprojects/subproject'
        subprojects = []
        for node in self.tree.xpath(query):
            subprojects.append(node.text)
        return subprojects
        
    @check_errors
    def parse_repositories(self, project=None):
        repo_config = os.path.join(os.environ.get('PVN_HOME'), self.repo_config)
        tree = parse_xml(repo_config)
        PymParser.check_version(tree, repo_config)
        self.directory_repo_parser.parse_available_repositories(tree)
        return self.directory_repo_parser.parse(self.tree)
        
    @check_errors
    def parse_artifacts(self, project=None):
        return self.artifacts_parser.parse(self.tree)
        
    @check_errors
    def parse_packages(self, project=None):
        return self.packages_parser.parse(self.tree)
        
    @check_errors_processes
    def parse_processes(self, scope, xpath, project=None):
        processes = []
        for node in self.tree.xpath('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/' + xpath + '[@scope="' + scope + '"]'):
            type = node.get('type')
            if type is None:
                raise ParserException('Missing process type')
            name = node.get('name')
            if name is None:
                raise ParserException('Missing process name')
            parser = self.plugins_manager.get_parser(type, os.path.dirname(self.pym))
            processes.extend(parser.parse(node, project))
        return processes

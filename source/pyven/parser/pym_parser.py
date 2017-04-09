import os
from pyven.logging.logger import Logger

from lxml import etree

import pyven.constants

from pyven.exceptions.parser_exception import ParserException

from pyven.checkers.checker import Checker
from pyven.plugins.manager import PluginsManager

from pyven.parser.constants_parser import ConstantsParser
from pyven.parser.directory_repo_parser import DirectoryRepoParser
from pyven.parser.artifacts_parser import ArtifactsParser
from pyven.parser.packages_parser import PackagesParser
from pyven.parser.makefile_parser import MakefileParser
from pyven.parser.unit_tests_parser import UnitTestsParser
from pyven.parser.valgrind_tests_parser import ValgrindTestsParser
from pyven.parser.integration_tests_parser import IntegrationTestsParser

class PymParser(object):
    
    def __init__(self, pym='pym.xml', plugins={}):
        self.pym = pym
        self.plugins_manager = PluginsManager(plugins)
        self.repo_config = 'repositories.xml'
        self.tree = None
        self.checker = Checker('Parser')
        self.constants_parser = ConstantsParser('/pyven/constants/constant', os.path.dirname(self.pym))
        self.directory_repo_parser = DirectoryRepoParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/repositories/repository', os.path.dirname(self.pym))
        self.artifacts_parser = ArtifactsParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/artifacts/artifact', os.path.dirname(self.pym))
        self.packages_parser = PackagesParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/packages/package', os.path.dirname(self.pym))
        self.makefile_parser = MakefileParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/build/tools', os.path.dirname(self.pym))
        self.unit_tests_parser = UnitTestsParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/tests/test[@type="unit"]', os.path.dirname(self.pym))
        self.valgrind_tests_parser = ValgrindTestsParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/tests/test[@type="valgrind"]', os.path.dirname(self.pym))
        self.integration_tests_parser = IntegrationTestsParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/tests/test[@type="integration"]', os.path.dirname(self.pym))
    
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
        
    @staticmethod
    def parse_xml(file):
        tree = None
        if not os.path.isfile(file):
            raise ParserException('Configuration file not available : ' + file)
        try:
            tree = etree.parse(file)
        except Exception as e:
            pyven_exception = ParserException('')
            pyven_exception.args = e.args
            raise pyven_exception
        return tree
    
    def check_errors(function):
        def _intern(self):
            try:
                return function(self)
            except ParserException as e:
                self.checker.errors.append(e.args)
                raise e
        return _intern
    
    @check_errors
    def parse_pym(self):
        Logger.get().info('Starting ' + self.pym + ' parsing')
        self.tree = PymParser.parse_xml(self.pym)
        PymParser.check_version(self.tree, self.pym)
        return True
        
    @check_errors
    def parse_plugins(self):
        if self.tree is not None:
            for plugin in self.tree.xpath('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/plugins/plugin'):
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
    def parse_project_title(self):
        title = ''
        if self.tree is not None:
            nodes = self.tree.xpath('/pyven/project')
            if len(nodes) > 0:
                title += nodes[0].text
        return title
        
    @check_errors
    def parse_constants(self):
        return self.constants_parser.parse(self.tree)
        
    @check_errors
    def parse_projects(self):
        query = '/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/subprojects/subproject'
        subprojects = []
        for node in self.tree.xpath(query):
            subprojects.append(node.text)
        return subprojects
        
    @check_errors
    def parse_repositories(self):
        repo_config = os.path.join(os.environ.get('PVN_HOME'), self.repo_config)
        tree = PymParser.parse_xml(repo_config)
        PymParser.check_version(tree, repo_config)
        self.directory_repo_parser.parse_available_repositories(tree)
        return self.directory_repo_parser.parse(self.tree)
        
    @check_errors
    def parse_artifacts(self):
        return self.artifacts_parser.parse(self.tree)
        
    @check_errors
    def parse_packages(self):
        return self.packages_parser.parse(self.tree)
        
    @check_errors
    def parse_preprocessors(self):
        preprocessors = []
        for node in self.tree.xpath('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/build/tools/tool[@scope="preprocess"]'):
            type = node.get('type')
            if type is None:
                raise ParserException('Missing pre-processor type')
            parser = self.plugins_manager.get_parser(type, os.path.dirname(self.pym))
            preprocessors.extend(parser.parse(node))
        return preprocessors
        
    @check_errors
    def parse_builders(self):
        builders = []
        for makefile_tools in self.makefile_parser.parse(self.tree):
            builders.extend(makefile_tools)
        for node in self.tree.xpath('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/build/tools/tool[@scope="build"]'):
            type = node.get('type')
            if type is None:
                raise ParserException('Missing builder type')
            parser = self.plugins_manager.get_parser(type, os.path.dirname(self.pym))
            builders.extend(parser.parse(node))
        return builders
        
    @check_errors
    def parse_postprocessors(self):
        postprocessors = []
        for node in self.tree.xpath('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/build/tools/tool[@scope="postprocess"]'):
            type = node.get('type')
            if type is None:
                raise ParserException('Missing post-processor type')
            parser = self.plugins_manager.get_parser(type, os.path.dirname(self.pym))
            postprocessors.extend(parser.parse(node))
        return postprocessors
        
    @check_errors
    def parse_unit_tests(self):
        return self.unit_tests_parser.parse(self.tree)
        
    @check_errors
    def parse_valgrind_tests(self):
        return self.valgrind_tests_parser.parse(self.tree)
        
    @check_errors
    def parse_integration_tests(self):
        return self.integration_tests_parser.parse(self.tree)

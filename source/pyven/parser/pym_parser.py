import os, sys
from pyven.logging.logger import Logger

from lxml import etree

import pyven.constants

from pyven.exceptions.parser_exception import ParserException

from pyven.checkers.checker import Checker

from pyven.parser.constants_parser import ConstantsParser
from pyven.parser.directory_repo_parser import DirectoryRepoParser
from pyven.parser.artifacts_parser import ArtifactsParser
from pyven.parser.packages_parser import PackagesParser
from pyven.parser.msbuild_parser import MSBuildParser
from pyven.parser.makefile_parser import MakefileParser
from pyven.parser.cmake_parser import CMakeParser
from pyven.parser.unit_tests_parser import UnitTestsParser
from pyven.parser.valgrind_tests_parser import ValgrindTestsParser
from pyven.parser.integration_tests_parser import IntegrationTestsParser

sys.path.append(os.path.join(os.environ.get('PVN_HOME'), 'plugins', 'command-plugin_1.0.0.zip'))
import command_plugin.parser

class PymParser(object):
    
    def __init__(self, pym='pym.xml'):
        self.pym = pym
        self.repo_config = 'repositories.xml'
        self.tree = None
        self.checker = Checker('Parser')
        self.constants_parser = ConstantsParser('/pyven/constants/constant', os.path.dirname(self.pym))
        self.directory_repo_parser = DirectoryRepoParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/repositories/repository', os.path.dirname(self.pym))
        self.artifacts_parser = ArtifactsParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/artifacts/artifact', os.path.dirname(self.pym))
        self.packages_parser = PackagesParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/packages/package', os.path.dirname(self.pym))
        self.cmake_parser = CMakeParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/build/tools', os.path.dirname(self.pym))
        self.msbuild_parser = MSBuildParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/build/tools', os.path.dirname(self.pym))
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
        for cmake_tools in self.cmake_parser.parse(self.tree):
            preprocessors.extend(cmake_tools)
        
        parser = command_plugin.parser.get(os.path.dirname(self.pym))
        for node in self.tree.xpath('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/build/tools/tool[@type="command" and @scope="preprocess"]'):
            preprocessors.extend(parser.parse(node))
        return preprocessors
        
    @check_errors
    def parse_builders(self):
        builders = []
        for msbuild_tools in self.msbuild_parser.parse(self.tree):
            builders.extend(msbuild_tools)
        for makefile_tools in self.makefile_parser.parse(self.tree):
            builders.extend(makefile_tools)
        parser = command_plugin.parser.get(os.path.dirname(self.pym))
        for node in self.tree.xpath('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/build/tools/tool[@type="command" and @scope="build"]'):
            builders.extend(parser.parse(node))
        return builders
        
    @check_errors
    def parse_postprocessors(self):
        postprocessors = []
        parser = command_plugin.parser.get(os.path.dirname(self.pym))
        for node in self.tree.xpath('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/build/tools/tool[@type="command" and @scope="postprocess"]'):
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

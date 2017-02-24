import logging, os

from lxml import etree

import pyven.constants

from pyven.exceptions.parser_exception import ParserException

from pyven.checkers.checker import Checker

from pyven.parser.constants_parser import ConstantsParser
from pyven.parser.directory_repo_parser import DirectoryRepoParser
from pyven.parser.artifacts_parser import ArtifactsParser
from pyven.parser.packages_parser import PackagesParser
from pyven.parser.msbuild_parser import MSBuildParser
from pyven.parser.cmake_parser import CMakeParser
from pyven.parser.command_parser import CommandParser
from pyven.parser.unit_tests_parser import UnitTestsParser
from pyven.parser.valgrind_tests_parser import ValgrindTestsParser
from pyven.parser.integration_tests_parser import IntegrationTestsParser

logger = logging.getLogger('global')

class PymParser(object):
	
	def __init__(self, pym='pym.xml'):
		self.pym = pym
		self.repo_config = 'repositories.xml'
		self.checker = Checker('Parser')
		self.constants_parser = ConstantsParser('/pyven/constants/constant')
		self.directory_repo_parser = DirectoryRepoParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/repositories/repository')
		self.artifacts_parser = ArtifactsParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/artifacts/artifact')
		self.packages_parser = PackagesParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/packages/package')
		self.cmake_parser = CMakeParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/build/tools')
		self.command_parser = CommandParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/build/tools')
		self.msbuild_parser = MSBuildParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/build/tools')
		self.unit_tests_parser = UnitTestsParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/tests/test[@type="unit"]')
		self.valgrind_tests_parser = ValgrindTestsParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/tests/test[@type="valgrind"]')
		self.integration_tests_parser = IntegrationTestsParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/tests/test[@type="integration"]')
		
	def _check_version(self, tree, file):
		doc_element = tree.getroot()
		if doc_element is None or doc_element.tag == "name":
			raise ParserException('[' + file + '] Missing "pyven" tag')
		expected_pyven_version = doc_element.get('version')
		if expected_pyven_version is None:
			raise ParserException('[' + file + '] Missing Pyven version information')
		if expected_pyven_version != pyven.constants.VERSION:
			raise ParserException('[' + file + '] Invalid Pyven version --> Expected : ' + expected_pyven_version + ', actual : ' + pyven.constants.VERSION)
		
	def _parse_xml(self, file):
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
		
	def parse(self):
		logger.info('Starting ' + self.pym + ' parsing')
		try:
			repo_config = os.path.join(os.environ.get('PVN_HOME'), self.repo_config)
			tree = self._parse_xml(repo_config)
			self._check_version(tree, repo_config)
			self.directory_repo_parser.parse_available_repositories(tree)
			
			tree = self._parse_xml(self.pym)
			self._check_version(tree, self.pym)
			
			constants = self.constants_parser.parse(tree)
			
			query = '/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/subprojects/subproject'
			subprojects = []
			for node in tree.xpath(query):
				subprojects.append(node.text)
			
			repositories = self.directory_repo_parser.parse(tree)
			artifacts = self.artifacts_parser.parse(tree)
			packages = self.packages_parser.parse(tree)
			
			preprocessors = []
			for cmake_tools in self.cmake_parser.parse(tree):
				preprocessors.extend(cmake_tools)
			
			builders = []
			for msbuild_tools in self.msbuild_parser.parse(tree):
				builders.extend(msbuild_tools)
			for command_tools in self.command_parser.parse(tree):
				builders.extend(command_tools)
			
			unit_tests = self.unit_tests_parser.parse(tree)
			valgrind_tests = self.valgrind_tests_parser.parse(tree)
			integration_tests = self.integration_tests_parser.parse(tree)
		
		except ParserException as e:
			self.checker.errors.append(e.args)
			raise e
			
		logger.info('pym.xml parsed successfully')
		return {'constants' : constants,\
				'subprojects' : subprojects,\
				'repositories' : repositories,\
				'artifacts' : artifacts,\
				'packages' : packages,\
				'preprocessors' : preprocessors,\
				'builders' : builders,\
				'unit_tests' : unit_tests,\
				'valgrind_tests' : valgrind_tests,\
				'integration_tests' : integration_tests}

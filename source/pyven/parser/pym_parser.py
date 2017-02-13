import logging, os

from lxml import etree

import pyven.constants

from pyven.exceptions.parser_exception import ParserException

from pyven.checkers.checker import Checker

from pyven.parser.directory_repo_parser import DirectoryRepoParser
from pyven.parser.artifacts_parser import ArtifactsParser
from pyven.parser.packages_parser import PackagesParser
from pyven.parser.msbuild_parser import MSBuildParser
from pyven.parser.cmake_parser import CMakeParser
from pyven.parser.unit_tests_parser import UnitTestsParser
from pyven.parser.valgrind_tests_parser import ValgrindTestsParser
from pyven.parser.integration_tests_parser import IntegrationTestsParser

logger = logging.getLogger('global')

class PymParser(object):
	
	def __init__(self, pym='pym.xml'):
		self.pym = pym
		self.checker = Checker('Parser')
		self.directory_repo_parser = DirectoryRepoParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/repositories/repository')
		self.artifacts_parser = ArtifactsParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/artifacts/artifact')
		self.packages_parser = PackagesParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/packages/package')
		self.cmake_parser = CMakeParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/build/tools')
		self.msbuild_parser = MSBuildParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/build/tools')
		self.unit_tests_parser = UnitTestsParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/tests/test[@type="unit"]')
		self.valgrind_tests_parser = ValgrindTestsParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/tests/test[@type="valgrind"]')
		self.integration_tests_parser = IntegrationTestsParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/tests/test[@type="integration"]')
		
	def parse(self):
		logger.info('Starting pym.xml parsing')
		try:
			if not os.path.isfile(self.pym):
				raise ParserException('No pym.xml file available in current directory')
			try:
				tree = etree.parse(self.pym)
			except Exception as e:
				pyven_exception = ParserException('')
				pyven_exception.args = e.args
				raise pyven_exception
			
			doc_element = tree.getroot()
			
			if doc_element is None or doc_element.tag == "name":
				raise ParserException('Missing "pyven" markup')
			expected_pyven_version = doc_element.get('version')
			if expected_pyven_version is None:
				raise ParserException('Missing Pyven version information')
			logger.info('Expected Pyven version : ' + expected_pyven_version)
			if expected_pyven_version != pyven.constants.VERSION:
				raise ParserException('Invalid Pyven version', 'Expected version : ' + expected_pyven_version, 'Version in use : ' + pyven.constants.VERSION)
			
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
			
			unit_tests = self.unit_tests_parser.parse(tree)
			valgrind_tests = self.valgrind_tests_parser.parse(tree)
			integration_tests = self.integration_tests_parser.parse(tree)
		
		except ParserException as e:
			self.checker.errors.append(e.args)
			raise e
			
		logger.info('pym.xml parsed successfully')
		return {'subprojects' : subprojects,\
				'repositories' : repositories,\
				'artifacts' : artifacts,\
				'packages' : packages,\
				'preprocessors' : preprocessors,\
				'builders' : builders,\
				'unit_tests' : unit_tests,\
				'valgrind_tests' : valgrind_tests,\
				'integration_tests' : integration_tests}

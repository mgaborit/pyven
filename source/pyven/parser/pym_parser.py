import logging, os

from lxml import etree

import pyven.constants

from pyven.exceptions.parser_exception import ParserException

from pyven.utils.factory import Factory
from pyven.checkers.checker import Checker

from pyven.parser.artifacts_parser import ArtifactsParser
from pyven.parser.packages_parser import PackagesParser
from pyven.parser.msbuild_parser import MSBuildParser
from pyven.parser.cmake_parser import CMakeParser

logger = logging.getLogger('global')

class PymParser(object):
	
	def __init__(self, pym='pym.xml'):
		self.pym = pym
		self.checker = Checker('Parser')
		self.artifacts_parser = ArtifactsParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/artifacts/artifact')
		self.packages_parser = PackagesParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/packages/package')
		self.cmake_parser = CMakeParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/build/tools')
		self.msbuild_parser = MSBuildParser('/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/build/tools')
		
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
			subprojects = self._parse_subprojects(tree, query)
			
			query = '/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/repositories/repository'
			repositories = self._parse(tree, 'repository', query)
			
			artifacts = self.artifacts_parser.parse(tree)
			packages = self.packages_parser.parse(tree)
			
			preprocessors = []
			for cmake_tools in self.cmake_parser.parse(tree):
				preprocessors.extend(cmake_tools)
			
			builders = []
			for msbuild_tools in self.msbuild_parser.parse(tree):
				builders.extend(msbuild_tools)
			
			query = '/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/tests/test[@type="unit"]'
			unit_tests = self._parse(tree, 'unit_test', query)
			
			query = '/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/tests/test[@type="valgrind"]'
			valgrind_tests = self._parse(tree, 'valgrind_test', query)
			
			query = '/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/tests/test[@type="integration"]'
			integration_tests = self._parse_integration_tests(tree, query)
		
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
	
	def _parse_subprojects(self, node, query):
		objects = []
		for descendant in node.xpath(query):
			objects.append(descendant.text)
		return objects
	
	def _parse(self, node, type, query):
		objects = []
		for descendant in node.xpath(query):
			objects.append(Factory.create(type, descendant))
		return objects
	
	def _parse_integration_tests(self, node, query):
		objects = []
		for descendant in node.xpath(query):
			packages = descendant.xpath('package')
			if len(packages) == 0:
				logger.error('Integration test : missing package')
			if len(packages) > 1:
				logger.error('Integration test : to many packages declared', 'Only one package can be added to integration test')
			objects.append({'integration_test' : Factory.create('integration_test', descendant), 'package' : packages[0].text})
		return objects
	
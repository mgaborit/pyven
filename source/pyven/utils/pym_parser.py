import logging, os

from lxml import etree

import pyven.constants
from pyven.exceptions.exception import PyvenException

from pyven.utils.factory import Factory
from pyven.utils.parser_checker import ParserChecker

logger = logging.getLogger('global')

class PymParser(object):
	
	def __init__(self, pym='pym.xml'):
		self.pym = pym
		self.checker = ParserChecker()
		
	def parse(self):
		logger.info('Starting pym.xml parsing')
		try:
			if not os.path.isfile(self.pym):
				raise PyvenException('No pym.xml file available in current directory')
			try:
				tree = etree.parse(self.pym)
			except Exception as e:
				pyven_exception = PyvenException('')
				pyven_exception.args = e.args
				raise pyven_exception
			
			doc_element = tree.getroot()
			
			if doc_element is None or doc_element.tag == "name":
				raise PyvenException('Missing "pyven" markup')
			expected_pyven_version = doc_element.get('version')
			if expected_pyven_version is None:
				raise PyvenException('Missing Pyven version information')
			logger.info('Expected Pyven version : ' + expected_pyven_version)
			if expected_pyven_version != pyven.constants.VERSION:
				raise PyvenException('Invalid Pyven version', 'Expected version : ' + expected_pyven_version, 'Version in use : ' + pyven.constants.VERSION)
			
			query = '/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/subprojects/subproject'
			subprojects = self._parse_subprojects(tree, query)
			
			query = '/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/repositories/repository'
			repositories = self._parse(tree, 'repository', query)
			
			query = '/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/artifacts/artifact'
			artifacts = self._parse(tree, 'artifact', query)
			
			query = '/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/packages/package'
			packages = self._parse_packages(tree, query)
			
			query = '/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/build/tools/tool[@scope="preprocess"]'
			preprocessors = self._parse(tree, 'preprocessor', query)
			
			query = '/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/build/tools/tool[@scope="build"]'
			builders = self._parse_builders(tree, query)
			
			query = '/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/tests/test[@type="unit"]'
			unit_tests = self._parse(tree, 'unit_test', query)
			
			query = '/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/tests/test[@type="valgrind"]'
			valgrind_tests = self._parse(tree, 'valgrind_test', query)
			
			query = '/pyven/platform[@name="'+pyven.constants.PLATFORM+'"]/tests/test[@type="integration"]'
			integration_tests = self._parse_integration_tests(tree, query)
		
		except PyvenException as e:
			self.checker.errors.append(e.args)
			self.checker.enabled = True
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
	
	def _parse_builders(self, node, query):
		objects = []
		for descendant in node.xpath(query):
			if descendant.get('type') == 'msbuild':
				for project in descendant.xpath('projects/project'):
					objects.append(Factory.create('builder', descendant, project.text))
			else:
				objects.append(Factory.create('builder', descendant))
		return objects
	
	def _parse_packages(self, node, query):
		objects = []
		for descendant in node.xpath(query):
			items = descendant.xpath('item')
			objects.append({'package' : Factory.create('package', descendant), 'items' : [i.text for i in items]})
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
	
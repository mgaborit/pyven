from lxml import etree

from pyven.parser.tests_parser import TestsParser
from pyven.exceptions.parser_exception import ParserException

from pyven.processing.tests.integration import IntegrationTest

class IntegrationTestsParser(TestsParser):
	TYPES = ['file']
	
	def __init__(self, query, path):
		super(IntegrationTestsParser, self).__init__(query, path)
		
	def _parse(self, node):
		members = super(IntegrationTestsParser, self)._parse(node)
		errors = []
		packages = node.xpath('package')
		if len(packages) == 0:
			errors.append('Integration test : missing package')
		if len(packages) > 1:
			errors.append('Integration test : to many packages declared')
			errors.append('Only one package can be added to an integration test')
		package = packages[0].text
		if package == '':
			errors.append('Integration test : missing package')
		if len(errors) > 0:
			e = ParserException('')
			e.args = tuple(errors)
			raise e
		return IntegrationTest(self.path, members['type'], members['report'], members['path'], members['filename'], members['arguments'], members['format'], package)

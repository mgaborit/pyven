from pyven.parser.tests_parser import TestsParser
from pyven.exceptions.parser_exception import ParserException

from pyven.processing.tests.valgrind import ValgrindTest

class ValgrindTestsParser(TestsParser):
	TYPES = ['file']
	
	def __init__(self, query):
		super(ValgrindTestsParser, self).__init__(query)
		
	def _parse(self, node):
		members = super(ValgrindTestsParser, self)._parse(node)
		return UnitTest(members['type'], members['path'], members['filename'], members['arguments'], members['format'])

from pyven.parser.tests_parser import TestsParser

from pyven.processing.tests.valgrind import ValgrindTest

class ValgrindTestsParser(TestsParser):
	TYPES = ['file']
	
	def __init__(self, query, path):
		super(ValgrindTestsParser, self).__init__(query, path)
		
	def _parse(self, node):
		members = super(ValgrindTestsParser, self)._parse(node)
		return ValgrindTest(self.path, members['type'], members['path'], members['filename'], members['arguments'], members['format'])

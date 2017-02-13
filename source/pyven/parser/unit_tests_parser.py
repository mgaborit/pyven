import logging
from lxml import etree

from pyven.parser.tests_parser import TestsParser
from pyven.exceptions.parser_exception import ParserException

from pyven.processing.tests.unit import UnitTest

class UnitTestsParser(TestsParser):
	TYPES = ['file']
	
	def __init__(self, query):
		super(UnitTestsParser, self).__init__(query)
		
	def _parse(self, node):
		members = super(UnitTestsParser, self)._parse(node)
		return UnitTest(members['type'], members['path'], members['filename'], members['arguments'], members['format'])

import os

from lxml import etree
from pyven.exceptions.parser_exception import ParserException
from pyven.parser.elements_parser import ElementsParser

class TestsParser(ElementsParser):
	TYPES = ['unit', 'integration', 'valgrind']
	
	def __init__(self, query, path):
		super(TestsParser, self).__init__(query, path)
	
	def _parse(self, node):
		errors = []
		members = {}
		type = node.get('type')
		if type is None:
			errors.append('Missing test type')
		if type not in TestsParser.TYPES:
			errors.append('Wrong test type : ' + type + ', available types : ' + str(TestsParser.TYPES))
		file = node.find('file').text
		if file == '':
			errors.append('Missing test executable file')
		(path, filename) = os.path.split(file)
		arguments = []
		for argument in node.xpath('arguments/argument'):
			arguments.append(argument.text)
		format = 'cppunit'
		if len(errors) > 0:
			e = ParserException('')
			e.args = tuple(errors)
			raise e
		members['type'] = type
		members['path'] = path
		members['filename'] = filename
		members['arguments'] = arguments
		members['format'] = format
		members['report'] = node.get('report')
		return members

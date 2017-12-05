from pyven.exceptions.parser_exception import ParserException
from pyven.parser.elements_parser import ElementsParser

class ConstantsParser(ElementsParser):

	def __init__(self, query, path):
		super(ConstantsParser, self).__init__(query, path)
		
	def parse(self, tree):
		constants = {}
		for node in tree.xpath(self.query):
			try:
				name = node.get('name')
				if name is None:
					raise ParserException('Missing constant name')
				if name in constants.keys():
					raise ParserException('Constant already declared : ' + name)
				constants[name] = node.text
			except ParserException as e:
				raise e
		return constants
from lxml import etree
from pyven.exceptions.parser_exception import ParserException
from pyven.parser.elements_parser import ElementsParser

class ToolsParser(ElementsParser):
	TYPES = ['msbuild', 'cmake', 'makefile']
	SCOPES = ['preprocess', 'build']
	
	def __init__(self, query):
		super(ToolsParser, self).__init__(query)
	
	def _parse(self, node):
		errors = []
		members = {}
		type = node.get('type')
		if type is None:
			errors.append('Missing tool type')
		elif type not in ToolsParser.TYPES:
			errors.append('Invalid tool type : ' + type + ', available tools : ' + str(Tool.TYPES))
		name = node.get('name')
		if name is None:
			errors.append('Missing tool name')
		scope = node.get('scope')
		if scope is None:
			errors.append('Missing tool scope')
		elif scope not in ToolsParser.SCOPES:
			errors.append('Invalid tool scope : ' + scope + ', available scopes : ' + str(Tool.SCOPES))
		members['type'] = type
		members['name'] = name
		members['scope'] = scope
		if len(errors) > 0:
			e = ParserException('')
			e.args = tuple(errors)
			raise e
		return members

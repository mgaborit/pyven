from pyven.exceptions.parser_exception import ParserException
from pyven.parser.tools_parser import ToolsParser
from pyven.processing.tools.command import CommandTool

class CommandParser(ToolsParser):
	
	def __init__(self, query):
		super(CommandParser, self).__init__(query)
	
	def _parse(self, node):
		objects = []
		for tool_node in node.xpath('tool[@type="command"]'):
			members = super(CommandParser, self)._parse(tool_node)
			errors = []
			directory_node = tool_node.find('directory')
			directory = '.'
			if directory_node is not None:
				directory = directory_node.text
			command_node = tool_node.find('command')
			if command_node is None:
				errors.append('Missing command')
			else:
				command = command_node.text
			if len(errors) > 0:
				e = ParserException('')
				e.args = tuple(errors)
				raise e
			objects.append(CommandTool(members['type'], members['name'], members['scope'], command, directory))
		return objects
		
		

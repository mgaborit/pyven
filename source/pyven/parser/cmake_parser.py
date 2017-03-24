from pyven.exceptions.parser_exception import ParserException
from pyven.parser.tools_parser import ToolsParser
from pyven.processing.tools.cmake import CMakeTool

class CMakeParser(ToolsParser):
	
	def __init__(self, query):
		super(CMakeParser, self).__init__(query)
	
	def _parse(self, node):
		objects = []
		for tool_node in node.xpath('tool[@scope="preprocess" and @type="cmake"]'):
			members = super(CMakeParser, self)._parse(tool_node)
			errors = []
			if members['scope'] != 'preprocess':
				errors.append('Invalid scope for CMake tool : ' + members['scope'])
			generator_node = tool_node.find('generator')
			if generator_node is None:
				errors.append('Missing CMake generator')
			else:
				generator = generator_node.text
			output_path_node = tool_node.find('output-path')
			if output_path_node is None:
				errors.append('Missing CMake output directory path')
			else:
				output_path = output_path_node.text
			definitions = []
			for definition in tool_node.xpath('definitions/definition'):
				definitions.append(definition.text)
			if len(errors) > 0:
				e = ParserException('')
				e.args = tuple(errors)
				raise e
			objects.append(CMakeTool(members['type'], members['report'], members['name'], members['scope'], generator, output_path, definitions))
		return objects
		
		

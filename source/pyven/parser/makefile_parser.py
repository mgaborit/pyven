from pyven.exceptions.parser_exception import ParserException
from pyven.parser.tools_parser import ToolsParser
from pyven.processing.tools.makefile import MakefileTool

class MakefileParser(ToolsParser):
	
	def __init__(self, query, path):
		super(MakefileParser, self).__init__(query, path)
	
	def _parse(self, node):
		objects = []
		for tool_node in node.xpath('tool[@scope="build" and @type="makefile"]'):
			members = super(MakefileParser, self)._parse(tool_node)
			errors = []
			if members['scope'] != 'build':
				errors.append('Invalid scope for makefile tool : ' + members['scope'])
			workspace_node = tool_node.find('workspace')
			if workspace_node is None:
				errors.append('Missing makefile workspace information')
			else:
				workspace = workspace_node.text
			rules_nodes = tool_node.xpath('rules/rule')
			rules = []
			if len(rules_nodes) == 0:
				errors.append('Missing makefile rules information informations')
			else:
				for rule_node in rules_nodes:
					rules.append(rule_node.text)
			options = []
			for option_node in tool_node.xpath('options/option'):
				options.append(option_node.text)
			if len(errors) > 0:
				e = ParserException('')
				e.args = tuple(errors)
				raise e
			objects.append(MakefileTool(self.path, members['type'], members['report'], members['name'], members['scope'], workspace, rules, options))
		return objects
		
		

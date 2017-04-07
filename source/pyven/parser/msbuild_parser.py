import os

from pyven.exceptions.parser_exception import ParserException
from pyven.parser.tools_parser import ToolsParser
from pyven.processing.tools.msbuild import MSBuildTool

class MSBuildParser(ToolsParser):
    
    def __init__(self, query, path):
        super(MSBuildParser, self).__init__(query, path)
    
    def _parse(self, node):
        objects = []
        for tool_node in node.xpath('tool[@scope="build" and @type="msbuild"]'):
            members = super(MSBuildParser, self)._parse(tool_node)
            errors = []
            if members['scope'] != 'build':
                errors.append('Invalid scope for MSBuild tool : ' + members['scope'])
            config_node = tool_node.find('configuration')
            if config_node is None:
                errors.append('Missing MSBuild configuration')
            else:
                configuration = config_node.text
            archi_node = tool_node.find('architecture')
            if archi_node is None:
                errors.append('Missing MSBuild platform')
            else:
                architecture = archi_node.text
            project_nodes = tool_node.xpath('projects/project')
            projects = []
            if len(project_nodes) == 0:
                errors.append('Missing projects informations')
            else:
                for project_node in project_nodes:
                    projects.append(project_node.text)
            options = []
            for option_node in tool_node.xpath('options/option'):
                options.append(option_node.text)
            if len(errors) > 0:
                e = ParserException('')
                e.args = tuple(errors)
                raise e
            for project in projects:
                objects.append(MSBuildTool(self.path, members['type'], members['report'], members['name'], members['scope'], configuration, architecture, project, options))
        return objects
        
        

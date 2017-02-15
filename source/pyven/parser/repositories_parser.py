import logging
from lxml import etree

from pyven.parser.elements_parser import ElementsParser
from pyven.exceptions.parser_exception import ParserException

class RepositoriesParser(ElementsParser):
	TYPES = ['file']
	
	def __init__(self, query):
		super(RepositoriesParser, self).__init__(query)
		
	def _parse(self, node):
		errors = []
		members = {}
		name = node.get('name')
		if name is None:
			errors.append('Missing repository name')
		type = node.get('type')
		if type is None:
			errors.append('Missing repository type')
		elif type not in RepositoriesParser.TYPES and type != 'workspace':
			errors.append('Invalid repository type : ' + type + ', available types : ' + str(RepositoriesParser.TYPES))
		url = node.get('url')
		if url is None:
			errors.append('Missing repository url')
		release = node.get('release')
		if release is None:
			release = False
		elif release == 'false':
			release = False
		elif release == 'true':
			release = True
		else:
			errors.append('Invalid value for "release" attribute : ' + release)
		members['type'] = type
		members['name'] = name
		members['url'] = url
		members['release'] = release
		if len(errors) > 0:
			e = ParserException('')
			e.args = tuple(errors)
			raise e
		return members

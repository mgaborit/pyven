from lxml import etree

from pyven.parser.elements_parser import ElementsParser
from pyven.exceptions.parser_exception import ParserException

class RepositoriesParser(ElementsParser):
	TYPES = ['file']
	
	def __init__(self, query, type_filter):
		super(RepositoriesParser, self).__init__(query)
		self.type_filter = type_filter
		self.available_repositories = {}
		
	def _parse(self, node):
		errors = []
		name = node.get('name')
		if name is None:
			errors.append('Missing repository name')
		elif name not in self.available_repositories.keys():
			errors.append('Repository not available : ' + name + ' --> Available repositories : ' + str([r for r in self.available_repositories.keys()]))
		if len(errors) > 0:
			e = ParserException('')
			e.args = tuple(errors)
			raise e
		return self.available_repositories[name]

	def _parse_available_repositories(self, node):
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
	
	def parse_available_repositories(self, tree):
		for node in tree.xpath(self.query + self.type_filter):
			try:
				repo = self._parse_available_repositories(node)
				self.available_repositories[repo.name] = repo
			except ParserException as e:
				raise e
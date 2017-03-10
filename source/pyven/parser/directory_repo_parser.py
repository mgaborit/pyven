import os
from lxml import etree

from pyven.parser.repositories_parser import RepositoriesParser
from pyven.exceptions.parser_exception import ParserException

from pyven.repositories.directory import DirectoryRepo

class DirectoryRepoParser(RepositoriesParser):
	def __init__(self, query, type_filter='[@type="file"]'):
		super(DirectoryRepoParser, self).__init__(query, type_filter)
	
	def _parse_available_repositories(self, node):
		members = super(DirectoryRepoParser, self)._parse_available_repositories(node)
		return DirectoryRepo(members['name'], members['type'], members['url'], members['release'])
	
	def parse_available_repositories(self, tree):
		super(DirectoryRepoParser, self).parse_available_repositories(tree)
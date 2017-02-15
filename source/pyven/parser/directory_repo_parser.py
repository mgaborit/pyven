import logging
from lxml import etree

from pyven.parser.repositories_parser import RepositoriesParser
from pyven.exceptions.parser_exception import ParserException

from pyven.repositories.directory import DirectoryRepo

class DirectoryRepoParser(RepositoriesParser):
	TYPES = ['file']
	
	def __init__(self, query):
		super(DirectoryRepoParser, self).__init__(query)
		
	def _parse(self, node):
		members = super(DirectoryRepoParser, self)._parse(node)
		return DirectoryRepo(members['name'], members['type'], members['url'], members['release'])

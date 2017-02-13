from pyven.parser.items_parser import ItemsParser
from pyven.exceptions.parser_exception import ParserException
from pyven.items.artifact import Artifact

class ArtifactsParser(ItemsParser):
	
	def __init__(self, query):
		super(ArtifactsParser, self).__init__(query)
		
	def _parse(self, node):
		members = super(ArtifactsParser, self)._parse(node)
		members['file'] = None
		if not members['to_retrieve']:
			members['file'] = node.text
		return Artifact(members['company'],\
						members['name'],\
						members['config'],\
						members['version'],\
						members['repo'],\
						members['to_retrieve'],\
						members['publish'],\
						members['file'])
		
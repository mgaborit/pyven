import os

from pyven.parser.items_parser import ItemsParser
from pyven.exceptions.parser_exception import ParserException
from pyven.items.artifact import Artifact

class ArtifactsParser(ItemsParser):
    
    def __init__(self, query, path):
        super(ArtifactsParser, self).__init__(query, path)
        
    def _parse(self, node):
        members = super(ArtifactsParser, self)._parse(node)
        members['file'] = None
        if not members['to_retrieve']:
            members['file'] = node.text
            if members['file'] is None:
                raise ParserException('Artifact ' + members['company'] + ':' + members['name'] + ':' + members['config'] + ':' + members['version'] + ' --> No repository nor filepath specified')
            else:
                members['file'] = os.path.join(self.path, members['file'])
        return Artifact(members['company'],\
                        members['name'],\
                        members['config'],\
                        members['version'],\
                        members['repo'],\
                        members['to_retrieve'],\
                        members['publish'],\
                        members['file'])
        
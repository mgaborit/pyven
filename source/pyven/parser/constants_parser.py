import os

from pyven.exceptions.parser_exception import ParserException
from pyven.parser.elements_parser import ElementsParser

from pyven.utils.utils import parse_xml

class ConstantsParser(ElementsParser):

    def __init__(self, path):
        super(ConstantsParser, self).__init__('//constants/constant', path)
        
    def parse(self, tree):
        constants = {}
        remote_constant_files = {}
        for node in tree.xpath(self.query):
            try:
                name = node.get('name')
                if name is None:
                    raise ParserException('Missing constant name')
                if name in constants.keys():
                    raise ParserException('Constant already declared : ' + name)
                is_local_node = node.get('local')
                is_local = (is_local_node is None) or (is_local_node != 'false')
                value = node.text
                if not is_local:
                    if value not in remote_constant_files.keys():
                        remote_constant_files[value] = []
                    remote_constant_files[value].append(name)
                else:
                    constants[name] = value
            except ParserException as e:
                raise e
        for f, remote_constant_names in remote_constant_files.items():
            try:
                tree = parse_xml(os.path.join(self.path, f))
                remote_constants = ConstantsParser(os.path.join(self.path, os.path.dirname(f))).parse(tree)
                for remote_constant_name in remote_constant_names:
                    if remote_constant_name not in remote_constants.keys():
                        raise ParserException('Constant not found : ' + remote_constant_name)
                    constants[remote_constant_name] = remote_constants[remote_constant_name]
            except ParserException as e:
                raise e
        return constants
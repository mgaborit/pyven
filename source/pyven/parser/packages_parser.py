from pyven.parser.items_parser import ItemsParser
from pyven.exceptions.parser_exception import ParserException
from pyven.items.package import Package

class PackagesParser(ItemsParser):
    
    def __init__(self, query):
        super(PackagesParser, self).__init__(query)
        
    def _parse(self, node):
        members = super(PackagesParser, self)._parse(node)
        members['extensions'] = []
        packages = node.xpath('extend')
        for package in packages:
            members['extensions'].append(package.text)
        items = node.xpath('item')
        if not members['to_retrieve'] and len(items) == 0 and len(members['extensions']) == 0:
            raise ParserException('Missing package items information')
        members['items'] = []
        for item in items:
            members['items'].append(item.text)
        delivery = ''
        if node.find('delivery') is not None:
            delivery = node.find('delivery').text
        if '$company' in delivery:
            delivery = delivery.replace('$$company', members['company'])
        if '$name' in delivery:
            delivery = delivery.replace('$$name', members['name'])
        if '$config' in delivery:
            delivery = delivery.replace('$$config', members['config'])
        if '$version' in delivery:
            delivery = delivery.replace('$$version', members['version'])
        members['delivery'] = delivery
        return Package(members['company'],\
                        members['name'],\
                        members['config'],\
                        members['version'],\
                        members['repo'],\
                        members['to_retrieve'],\
                        members['publish'],\
                        members['items'],\
                        members['delivery'],\
                        members['extensions'])
        
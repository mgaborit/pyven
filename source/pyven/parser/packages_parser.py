from pyven.parser.items_parser import ItemsParser
from pyven.exceptions.parser_exception import ParserException
from pyven.items.package import Package

class PackagesParser(ItemsParser):
    
    def __init__(self, query, path):
        super(PackagesParser, self).__init__(query, path)
        
    def _parse(self, node):
        members = super(PackagesParser, self)._parse(node)
        members['extensions'] = []
        packages = node.xpath('extend')
        for package in packages:
            members['extensions'].append(package.text)
        members['directories'] = []
        dirs = node.xpath('directory')
        for d in dirs:
            members['directories'].append(d.text)
        members['patterns'] = []
        patterns = node.xpath('pattern')
        for pattern in patterns:
            members['patterns'].append(pattern.text)
        items = node.xpath('item')
        if not members['to_retrieve'] and len(items) == 0\
            and len(members['extensions']) == 0\
            and len(members['patterns']) == 0\
            and len(members['directories']) == 0:
            raise ParserException('Missing package items information')
        members['items'] = []
        for item in items:
            members['items'].append(item.text)
        deliveries = []
        for delivery_node in node.xpath('delivery'):
            delivery = delivery_node.text
            if '$company' in delivery:
                delivery = delivery.replace('$$company', members['company'])
            if '$name' in delivery:
                delivery = delivery.replace('$$name', members['name'])
            if '$config' in delivery:
                delivery = delivery.replace('$$config', members['config'])
            if '$version' in delivery:
                delivery = delivery.replace('$$version', members['version'])
            deliveries.append(delivery)
        members['delivery'] = deliveries
        return Package(members['company'],\
                        members['name'],\
                        members['config'],\
                        members['version'],\
                        members['repo'],\
                        members['to_retrieve'],\
                        members['publish'],\
                        members['items'],\
                        members['delivery'],\
                        members['extensions'],\
                        self.path,\
                        members['patterns'],\
                        members['directories'])
        
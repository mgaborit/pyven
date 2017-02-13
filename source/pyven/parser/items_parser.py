from pyven.parser.elements_parser import ElementsParser
from pyven.exceptions.parser_exception import ParserException

class ItemsParser(ElementsParser):
	
	def __init__(self, query):
		super(ItemsParser, self).__init__(query)
	
	def _parse(self, node):
		errors = []
		members = {}
		members['company'] = node.get('company')
		if members['company'] is None:
			errors.append('Missing artifact or package company')
		members['name'] = node.get('name')
		if members['name'] is None:
			errors.append('Missing artifact or package name')
		members['config'] = node.get('config')
		if members['config'] is None:
			errors.append('Missing artifact or package config')
		members['version'] = node.get('version')
		if members['version'] is None:
			errors.append('Missing artifact or package version')
		members['repo'] = node.get('repo')
		members['to_retrieve'] = members['repo'] is not None
		if members['to_retrieve']:
			members['publish'] = False
		else:
			members['publish'] = True
		publish = node.get('publish')
		if publish is not None:
			if publish == 'true':
				members['publish'] = True
			elif publish == 'false':
				members['publish'] = False
			else:
				errors.append('Invalid value for "publish" attribute')
		if len(errors) > 0:
			e = ParserException('')
			e.args = tuple(errors)
			raise e
		return members

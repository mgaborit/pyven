from lxml import etree

from pyven.exceptions.parser_exception import ParserException

class ElementsParser(object):
	
	def __init__(self, query):
		self.query = query
		
	def _parse(self, node):
		raise NotImplementedError
		
	def parse(self, tree):
		objects = []
		for node in tree.xpath(self.query):
			try:
				objects.append(self._parse(node))
			except ParserException as e:
				#e.args = e.args + (etree.tostring(node, pretty_print=True).decode('utf-8').strip(' \t\n\r').replace('<', '&lt;').replace('>', '&gt;'), )
				raise e
		return objects
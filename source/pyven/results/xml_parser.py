import os
from lxml import etree

from pyven.results.results_parser import ResultsParser
from pyven.exceptions.exception import PyvenException

class XMLParser(ResultsParser):

	def __init__(self, format):
		super(XMLParser, self).__init__()
		self.tree = None
		self.format = format
	
	def parse(self, file):
		result = []
		if os.path.isfile(file):
			tree = etree.parse(file)
			doc_element = tree.getroot()
			if self.format == 'cppunit':
				result = self._parse_xml_cppunit(doc_element)
			else:
				raise PyvenException('Invalid XML format : ' + self.format)
		else:
			msg = ['XML report not found']
			self.errors.append(msg)
		return result
		
	def _parse_xml_cppunit(self, node):
		query = '/TestRun/FailedTests/FailedTest'
		for failed_test in node.xpath(query):
			msg = ['Test ' + failed_test.find('Name').text,\
					'Failure type : ' + failed_test.find('FailureType').text,\
					'Message : ' + failed_test.find('Message').text]
			self.errors.append(msg)

			
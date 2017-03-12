from lxml import etree

import pyven.constants
from pyven.reporting.content.listing import Listing
from pyven.reporting.content.lines import Lines
from pyven.reporting.content.error import Error
from pyven.reporting.content.warning import Warning
from pyven.reporting.content.title import Title
from pyven.reporting.content.properties import Properties
from pyven.reporting.content.success import Success
from pyven.reporting.content.failure import Failure
from pyven.reporting.content.unknown import Unknown

class Reportable(object):
	
	def __init__(self):
		self.status = pyven.constants.STATUS[2]
		self.errors = []
		self.warnings = []
	
	def status(self):
		raise NotImplementedError('Invalid call to ' + type(self).__name__ + ' abstract method "status"')

	@staticmethod
	def parse_logs(logs, tokens, exceptions):
		result = []
		for line in [l for l in logs]:
			i = 0
			found = False
			while not found and i < len(tokens):
				if tokens[i] in line:
					for exception in exceptions:
						if exception in line:
							found = True
					if not found:
						result.append([line])
						found = True
				else:
					i += 1
		return result

	@staticmethod
	def _parse_xml_cppunit(node):
		result = []
		query = '/TestRun/FailedTests/FailedTest'
		for failed_test in node.xpath(query):
			msg = ['Test ' + failed_test.find('Name').text,\
					'Failure type : ' + failed_test.find('FailureType').text,\
					'Message : ' + failed_test.find('Message').text]
			result.append(msg)
		return result

	@staticmethod
	def _parse_xml_valgrind(node):
		result = []
		return result

	@staticmethod
	def parse_xml(format, file):
		result = []
		tree = etree.parse(file)
		doc_element = tree.getroot()
		if format == 'cppunit':
			result = Reportable._parse_xml_cppunit(doc_element)
		if format == 'valgrind':
			result = Reportable._parse_xml_valgrind(doc_element)
		return result
			
	def content(self):
		lines = []
		for error in self.errors:
			lines.append(Error(error))
		for warning in self.warnings:
			lines.append(Warning(warning))
		content_lines = Lines(lines)
		return Listing(title=Title(self.title()),\
				status=self.report_status(),\
				properties=Properties(self.properties()),\
				lines=content_lines)
		
	def title(self):
		raise NotImplementedError
		
	def properties(self):
		raise NotImplementedError
		
	def report_status(self):
		if self.status == pyven.constants.STATUS[0]:
			return Success()
		elif self.status == pyven.constants.STATUS[1]:
			return Failure()
		else:
			return Unknown()
	
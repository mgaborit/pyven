from lxml import etree

class Reportable(object):
	
	def __init__(self):
		self.errors = []
		self.warnings = []
	
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
			

	def report_summary(self):
		raise NotImplementedError('Invalid call to ' + type(self).__name__ + ' abstract method "report_summary"')

	def report_identifiers(self):
		raise NotImplementedError('Invalid call to ' + type(self).__name__ + ' abstract method "report_identifiers"')

	def report_status(self):
		raise NotImplementedError('Invalid call to ' + type(self).__name__ + ' abstract method "report_status"')
		
	def report_properties(self):
		raise NotImplementedError('Invalid call to ' + type(self).__name__ + ' abstract method "report_properties"')

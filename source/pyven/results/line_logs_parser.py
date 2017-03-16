from pyven.results.logs_parser import LogsParser

class LineLogsParser(LogsParser):

	def __init__(self, error_patterns=[], error_exceptions=[], warning_patterns=[], warning_exceptions=[]):
		super(LineLogsParser, self).__init__()
		self.error_patterns = error_patterns
		self.error_exceptions = error_exceptions
		self.warning_patterns = warning_patterns
		self.warning_exceptions = warning_exceptions
		
	def parse(self, results):
		self.errors = LineLogsParser._parse(results, self.error_patterns, self.error_exceptions)
		self.warnings = LineLogsParser._parse(results, self.warning_patterns, self.warning_exceptions)
		
	@staticmethod
	def _parse(logs, patterns, exceptions):
		result = []
		for line in logs:
			i = 0
			found = False
			while not found and i < len(patterns):
				if patterns[i] in line:
					for exception in exceptions:
						if exception in line:
							found = True
					if not found:
						result.append([line])
						found = True
				else:
					i += 1
		return result
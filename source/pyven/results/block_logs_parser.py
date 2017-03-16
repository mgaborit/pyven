from pyven.results.logs_parser import LogsParser

class BlockLogsParser(LogsParser):

	def __init__(self, begin_error_patterns, end_error_patterns, begin_warning_patterns=[], end_warning_patterns=[]):
		super(BlockLogsParser, self).__init__()
		self.begin_error_patterns = begin_error_patterns
		self.end_error_patterns = end_error_patterns
		self.begin_warning_patterns = begin_warning_patterns
		self.end_warning_patterns = end_warning_patterns
		
	def parse(self, results):
		self.errors = BlockLogsParser._parse(results, self.begin_error_patterns, self.end_error_patterns)
		self.warnings = BlockLogsParser._parse(results, self.begin_warning_patterns, self.end_warning_patterns)
		
	@staticmethod
	def _parse(logs, begin, end):
		result = []
		adding = False
		item = []
		for line in logs:
			found_pattern = False
			if not adding:
				i = 0
				while not found_pattern and i < len(begin):
					if begin[i] in line:
						found_pattern = True
						adding = True
					else:
						i += 1
			if adding:
				i = 0
				item.append(line)
				while not found_pattern and i < len(end):
					if end[i] in line:
						found_pattern = True
						adding = False
						result.append(item)
						item = []
					else:
						i += 1
		if adding:
			result.append(item)
		return result
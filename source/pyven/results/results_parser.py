class ResultsParser(object):

	def __init__(self):
		self.errors = []
		self.warnings = []
		
	def parse(self, results):
		raise NotImplementedError

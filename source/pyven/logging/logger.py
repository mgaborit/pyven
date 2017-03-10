import logging

class Logger:
	COUNT = 0
	SINGLETON = None
	
	def __init__(self):
		Logger.COUNT += 1
		self.project = None
		self.level = logging.DEBUG
	
		self.default_formatter = logging.Formatter('[%(levelname)s] %(message)s')
		
		self.stream_handler = logging.StreamHandler()
		self.stream_handler.setLevel(logging.DEBUG)
		self.stream_handler.setFormatter(self.default_formatter)
		
		logger = logging.getLogger('global')
		logger.setLevel(self.level)
		logger.addHandler(self.stream_handler)

	@staticmethod
	def get():
		if Logger.COUNT == 0 and Logger.SINGLETON is None:
			Logger.SINGLETON = Logger()
			
		if Logger.SINGLETON.project is None or Logger.SINGLETON.project.path == '.':
			Logger.SINGLETON.stream_handler.setFormatter(Logger.SINGLETON.default_formatter)
		else:
			Logger.SINGLETON.stream_handler.setFormatter(logging.Formatter('[%(levelname)s] [' + Logger.SINGLETON.project.path + '] %(message)s'))

		return logging.getLogger('global')
		
	@staticmethod
	def set_format(project=None):
		Logger.SINGLETON.project = project
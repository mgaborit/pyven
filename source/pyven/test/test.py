import subprocess, logging, os

logger = logging.getLogger('global')

# pym.xml 'test' node
class Test(object):

	def __init__(self, node):
		(self.path, self.filename) = os.path.split(node.find('file').text)
		self.arguments = []
		for argument in node.xpath('arguments/argument'):
			self.arguments.append(argument.text)
	
	def _format_call(self):
		call = [self.filename]
		for argument in self.arguments:
			call.append(argument)
			
		return call
	
	def run(self, verbose=False):
		FNULL = open(os.devnull, 'w')
		cwd = os.getcwd()
		if os.path.isdir(self.path):
			logger.info('Entering test directory : ' + self.path)
			os.chdir(self.path)
			logger.info('Running test : ' + self.filename)
			if verbose:
				subprocess.call(self._format_call())
			else:
				subprocess.call(self._format_call(), stdout=FNULL, stderr=subprocess.STDOUT)
			os.chdir(cwd)
		else:
			logger.error('Unknown directory : ' + self.path)
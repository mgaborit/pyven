import subprocess, logging, os

from pyven.exception import PyvenException

logger = logging.getLogger('global')

# pym.xml 'test' node
class Test(object):
	AVAILABLE_TYPES = ['unit', 'integration']

	def __init__(self, node):
		self.type = node.get('type')
		if self.type is None:
			raise PyvenException('Missing test type')
		if self.type not in Test.AVAILABLE_TYPES:
			raise PyvenException('Wrong test type : ' + self.type, 'Available types : ' + str(Test.AVAILABLE_TYPES))
		(self.path, self.filename) = os.path.split(node.find('file').text)
		self.arguments = []
		for argument in node.xpath('arguments/argument'):
			self.arguments.append(argument.text)
	
	def _format_call(self):
		if os.name == 'nt':
			call = [self.filename]
		elif os.name == 'posix':
			call = ['./' + self.filename]
		for argument in self.arguments:
			call.append(argument)
		return call

	def _copy_resources(self, repo=None, resources=None):
		pass
		
	def run(self, verbose=False, repo=None, resources=None):
		if not os.path.isfile(os.path.join(self.path, self.filename)):
			raise PyvenException('Test file not found : ' + os.path.join(self.path, self.filename))
		self._copy_resources(repo, resources)
		FNULL = open(os.devnull, 'w')
		cwd = os.getcwd()
		if os.path.isdir(self.path):
			logger.info('Entering test directory : ' + self.path)
			os.chdir(self.path)
			logger.info('Running test : ' + self.filename)
			if verbose:
				return_code = subprocess.call(self._format_call())
			else:
				return_code = subprocess.call(self._format_call(), stdout=FNULL, stderr=subprocess.STDOUT)
			os.chdir(cwd)
			if return_code != 0:
				logger.error('Test failed : ' + self.filename)
				return False
			logger.info('Test OK : ' + self.filename)
			return True
		logger.error('Unknown directory : ' + self.path)
		return False
		
	def factory(node):
		type = node.get('type')
		if type is None:
			raise PyvenException('Missing test type')
		if type not in Test.AVAILABLE_TYPES:
			raise PyvenException('Wrong test type : ' + type, 'Available test types : ' + str(Test.AVAILABLE_TYPES))
		if type == "unit": return UnitTest(node)
		if type == "integration": return IntegrationTest(node)
	factory = staticmethod(factory)
	
class IntegrationTest(Test):

	def __init__(self, node):
		super(IntegrationTest,self).__init__(node)
		packages = node.xpath('package')
		if len(packages) < 1:
			raise PyvenException('Missing package for test : ' + os.path.join(self.path, self.filename))
		if len(packages) > 1:
			raise PyvenException('Too many packages specified for test : ' + os.path.join(self.path, self.filename))
		self.package = packages[0].text
		
	def _copy_resources(self, repo=None, resources=None):
		if self.package in resources.keys():
			package = resources[self.package]
			package.unpack(self.path, repo, flatten=True)
		else:
			raise PyvenException('Package not found : ' + self.package)
		
class UnitTest(Test):

	def __init__(self, node):
		super(UnitTest,self).__init__(node)

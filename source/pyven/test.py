import subprocess, logging, os, time

from pyven.exception import PyvenException

logger = logging.getLogger('global')

# pym.xml 'test' node
class Test(object):
	AVAILABLE_TYPES = ['unit', 'integration']
	STATUS = ['SUCCESS', 'FAILURE']

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
		self.errors = []
		self.status = Test.STATUS[0]
		self.duration = 0
	
	def report_id(self):
		return self.type + ':' + self.filename
	
	def report_summary_description(self):
		return os.path.join(self.path, self.filename)
		
	def report_error(self, error):
		html_str = '<div class="errorDiv">'
		html_str += '<span class="error">' + error + '</span>'
		html_str += '</div>'
		return html_str
	
	def _report_informations(self):
		html_str = '<h2>' + self.type + ' test : ' + os.path.join(self.path, self.filename) + '</h2>'
		html_str += '<div class="propertiesDiv">'
		if self.status == Test.STATUS[0]:
			html_str += '<p class="property">Status : <span class="success">' + self.status + '</span></p>'
		elif self.status == Test.STATUS[1]:
			html_str += '<p class="property">Status : <span class="failure">' + self.status + '</span></p>'
		html_str += '<p class="property">Duration : ' + str(self.duration) + ' seconds</p>'
		html_str += '</div>'
		return html_str
	
	def _report(self, nb_lines):
		html_str = ''
		i = 0
		html_str += self._report_informations()
		for error in self.errors:
			if i < nb_lines:
				html_str += self.report_error(error)
				i += 1
		return html_str
	
	def report(self, nb_lines=10):
		html_str = '<div id="' + self.report_id() + '" class="stepDiv">'
		html_str += self._report(nb_lines)
		html_str += '</div>'
		return html_str
	
	def _parse_logs(self, logs, error_tokens, except_tokens):
		if os.name == 'nt':
			encoding = 'windows-1252'
		else:
			encoding = 'utf-8'
		for line in [l.decode(encoding) for l in logs]:
			i = 0
			found = False
			while not found and i < len(error_tokens):
				if error_tokens[i] in line:
					self.errors.append(line)
					found = True
				else:
					i += 1

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
			tic = time.time()
			sp = subprocess.Popen(self._format_call(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			toc = time.time()
			self.duration = round(toc - tic, 3)
			
			os.chdir(cwd)
			out, err = sp.communicate()
			
			if verbose:
				for line in out.splitlines():
					logger.info(line)
				for line in err.splitlines():
					logger.info(line)
				
			if sp.returncode != 0:
				self.status = Test.STATUS[1]
				self._parse_logs([out], ['assertion', 'error'], [])
				logger.error('Test failed : ' + self.filename)
			else:
				logger.info('Test OK : ' + self.filename)
			return sp.returncode == 0
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

	
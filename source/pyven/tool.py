import subprocess, os, logging, shutil

logger = logging.getLogger('global')

# pym.xml 'tool' node
class Tool(object):
	AVAILABLE_TOOLS = ['cmake', 'msbuild', 'command']
	AVAILABLE_SCOPES = ['preprocess', 'build']
	
	def __init__(self, node):
		self.type = node.get('type')
		if self.type not in Tool.AVAILABLE_TOOLS:
			raise Exception('Wrong tool type : ' + self.type, 'Available tools : ' + str(Tool.AVAILABLE_TOOLS))
		self.name = node.get('name')
		self.scope = node.get('scope')
		if self.scope not in Tool.AVAILABLE_SCOPES:
			raise Exception('Wrong tool scope : ' + self.scope, 'Available scopes : ' + str(Tool.AVAILABLE_SCOPES))
		
	def _format_call(self):
		raise NotImplementedError
	
	def process(self):
		raise NotImplementedError
		
	def clean(self, verbose=False):
		raise NotImplementedError
		
	def factory(node):
		type = node.get('type')
		if type not in Tool.AVAILABLE_TOOLS:
			raise Exception('Wrong tool type : ' + type, 'Available tools : ' + str(Tool.AVAILABLE_TOOLS))
		if type == "cmake": return CMakeTool(node)
		if type == "msbuild": return MSBuildTool(node)
		if type == "command": return CommandTool(node)
	factory = staticmethod(factory)
	
class CMakeTool(Tool):

	def __init__(self, node):
		super(CMakeTool, self).__init__(node)
		self.generator = node.find('generator').text
		self.output_path = node.find('output-path').text
		self.definitions = []
		for definition in node.xpath('definitions/definition'):
			self.definitions.append(definition.text)
		if self.scope == 'build':
			logger.warning('CMake will be called during build but not preprocessing')
	
	def _format_call(self):
		call = [self.type, '-H.', '-B'+self.output_path, '-G'+self.generator+'']
		for definition in self.definitions:
			call.append('-D'+definition)
			
		return call
	
	def process(self, verbose=False):
		FNULL = open(os.devnull, 'w')
		logger.info('Preprocessing : ' + self.type + ':' + self.name)
		if verbose:
			return_code = subprocess.call(self._format_call())
		else:
			return_code = subprocess.call(self._format_call(), stdout=FNULL, stderr=subprocess.STDOUT)
			
		if return_code != 0:
			logger.error('Preprocessing failed : ' + self.type + ':' + self.name)
			return False
		return True
	
	def clean(self, verbose=False):
		logger.info('Cleaning : ' + self.type + ':' + self.name)
		if os.path.isdir(self.output_path):
			shutil.rmtree(self.output_path)
		return True
		
class MSBuildTool(Tool):

	def __init__(self, node):
		super(MSBuildTool, self).__init__(node)
		self.configuration = node.find('configuration').text
		self.architecture = node.find('architecture').text
		self.projects = []
		for project in node.xpath('projects/project'):
			self.projects.append(project.text)
		self.options = []
		for option in node.xpath('options/option'):
			self.arguments.append(option.text)
		if self.scope == 'preprocess':
			logger.warning('MSBuild will be called during preprocessing but not build')
		
	def _format_call(self, project, clean=False):
		call = ['msbuild.exe', project, '/p:config='+self.configuration, '/p:platform='+self.architecture]
		if clean:
			call.append('/t:clean')
		else:
			call.append('/t:build')
		for option in self.options:
			call.append(option)
			
		return call
	
	def process(self, verbose=False):
		FNULL = open(os.devnull, 'w')
		logger.info('Building : ' + self.type + ':' + self.name)
		for project in self.projects:
			if verbose:
				return_code = subprocess.call(self._format_call(project))
			else:
				return_code = subprocess.call(self._format_call(project), stdout=FNULL, stderr=subprocess.STDOUT)
		if return_code != 0:
			logger.error('Build failed : ' + self.type + ':' + self.name)
			return False
		return True
		
	def clean(self, verbose=False):
		FNULL = open(os.devnull, 'w')
		logger.info('Cleaning : ' + self.type + ':' + self.name)
		for project in self.projects:
			if verbose:
				return_code = subprocess.call(self._format_call(project, clean=True))
			else:
				return_code = subprocess.call(self._format_call(project, clean=True), stdout=FNULL, stderr=subprocess.STDOUT)
		if return_code != 0:
			logger.error('Clean failed : ' + self.type + ':' + self.name)
			return False
		return True
			
class CommandTool(Tool):

	def __init__(self, node):
		super(CommandTool, self).__init__(node)
		programs = node.xpath('program')
		if len(programs) < 1:
			raise Exception('Missing program')
		if len(programs) > 1:
			raise Exception('Too many programs specified')
		self.program = programs[0]
		self.arguments = []
		for argument in node.xpath('arguments/argument'):
			self.arguments.append(argument.text)
		
	def _format_call(self):
		call = [self.program]
		for argument in self.arguments:
			call.append(argument)
			
		return call
	
	def process(self, verbose=False):
		FNULL = open(os.devnull, 'w')
		logger.info('Command called : ' + self.type + ':' + self.name)
		if verbose:
			return_code = subprocess.call(self._format_call())
		else:
			return_code = subprocess.call(self._format_call(), stdout=FNULL, stderr=subprocess.STDOUT)
		if return_code != 0:
			logger.error('Command failed : ' + self.type + ':' + self.name)
			return False
		return True
		
	def clean(self, verbose=False):
		pass
		
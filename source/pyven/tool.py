import subprocess, os, logging

logger = logging.getLogger('global')

# pym.xml 'tool' node
class Tool(object):
	AVAILABLE_TOOLS = ['cmake', 'msbuild']
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
		
	def factory(node):
		type = node.get('type')
		if type not in Tool.AVAILABLE_TOOLS:
			raise Exception('Wrong tool type : ' + type, 'Available tools : ' + str(Tool.AVAILABLE_TOOLS))
		if type == "cmake": return CMakeTool(node)
		if type == "msbuild": return MSBuildTool(node)
	factory = staticmethod(factory)
	
class CMakeTool(Tool):

	def __init__(self, node):
		super(CMakeTool, self).__init__(node)
		self.generator = node.find('generator').text
		self.output_path = node.find('output-path').text
		self.definitions = []
		for definition in node.xpath('definitions/definition'):
			self.definitions.append(definition.text)
	
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
		
	def _format_call(self, project):
		call = ['msbuild.exe', project, '/property:Configuration='+self.configuration, '/property:Platform='+self.architecture]
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
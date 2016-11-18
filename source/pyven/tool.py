import subprocess, os, logging

logger = logging.getLogger('global')

# pym.xml 'tool' node
class Tool(object):
	AVAILABLE_TOOLS = ['cmake', 'msbuild']
	AVAILABLE_SCOPES = ['preprocess', 'build']
	
	def __init__(self, node):
		self.name = node.get('name')
		if self.name not in Tool.AVAILABLE_TOOLS:
			raise Exception('Wrong tool : ' + self.name, 'Available tools : ' + str(Tool.AVAILABLE_TOOLS))
		self.configuration = node.get('configuration')
		self.scope = node.get('scope')
		if self.scope not in Tool.AVAILABLE_SCOPES:
			raise Exception('Wrong tool type : ' + self.scope, 'Available scopes : ' + str(Tool.AVAILABLE_SCOPES))
		
	def _format_call(self):
		raise NotImplementedError
	
	def process(self):
		raise NotImplementedError
		
	def factory(node):
		name = node.get('name')
		if name not in Tool.AVAILABLE_TOOLS:
			raise Exception('Wrong tool : ' + name, 'Available tools : ' + str(Tool.AVAILABLE_TOOLS))
		if name == "cmake": return CMakeTool(node)
		if name == "msbuild": return MSBuildTool(node)
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
		call = [self.name, '-H.', '-B'+self.output_path, '-G'+self.generator+'']
		for definition in self.definitions:
			call.append('-D'+definition)
			
		return call
	
	def process(self, verbose=False):
		FNULL = open(os.devnull, 'w')
		logger.info('Preprocessing : ' + self.name + ':' + self.configuration)
		if verbose:
			return_code = subprocess.call(self._format_call())
		else:
			return_code = subprocess.call(self._format_call(), stdout=FNULL, stderr=subprocess.STDOUT)
			
		if return_code != 0:
			logger.error('Preprocessing failed : ' + self.name + ':' + self.configuration)
			return False
		return True
		
class MSBuildTool(Tool):

	def __init__(self, node):
		super(MSBuildTool, self).__init__(node)
		self.project_file = node.find('project-file').text
		self.configuration = node.find('configuration').text
		self.architecture = node.find('architecture').text
		self.arguments = []
		for argument in node.xpath('arguments/argument'):
			self.arguments.append(argument.text)
		
	def _format_call(self):
		call = ['msbuild.exe', self.project_file, '/property:Configuration='+self.configuration, '/property:Platform='+self.architecture]
		for argument in self.arguments:
			call.append(argument)
			
		return call
	
	def process(self, verbose=False):
		FNULL = open(os.devnull, 'w')
		logger.info('Building : ' + self.name + ':' + self.configuration)
		if verbose:
			return_code = subprocess.call(self._format_call())
		else:
			return_code = subprocess.call(self._format_call(), stdout=FNULL, stderr=subprocess.STDOUT)
		
		if return_code != 0:
			logger.error('Build failed : ' + self.name + ':' + self.configuration)
			return False
		return True
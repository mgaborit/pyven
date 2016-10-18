import subprocess, os, logging

logger = logging.getLogger('global')

# pym.xml 'tool' node
class Tool(object):

	def __init__(self, node):
		self.name = node.get('name')
		self.id = node.get('id')
		self.scope = node.get('scope')
		
	def _format_call(self):
		raise NotImplementedError('unimplemented method')
	
	def process(self):
		raise NotImplementedError('Invalid call')
		
	def factory(node):
		if node.get('name') == "cmake": return CMakeTool(node)
		if node.get('name') == "msbuild": return MSBuildTool(node)
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
		logger.info('Preprocessing with : ' + self.name + ':' + self.id)
		if verbose:
			return_code = subprocess.call(self._format_call())
		else:
			return_code = subprocess.call(self._format_call(), stdout=FNULL, stderr=subprocess.STDOUT)
			
		if return_code != 0:
			logger.error('Preprocessing terminated with errors')
		
class MSBuildTool(Tool):

	def __init__(self, node):
		super(MSBuildTool, self).__init__(node)
		self.project_file = node.find('project-file').text
		self.configuration = node.find('configuration').text
		self.architecture = node.find('architecture').text
		
	def process(self, verbose=False):
		FNULL = open(os.devnull, 'w')
		logger.info('Building with : ' + self.name + ':' + self.id)
		if verbose:
			return_code = subprocess.call(['msbuild.exe', self.project_file, '/property:Configuration='+self.configuration, '/property:Platform='+self.architecture])
		else:
			return_code = subprocess.call(['msbuild.exe', self.project_file, '/property:Configuration='+self.configuration, '/property:Platform='+self.architecture], stdout=FNULL, stderr=subprocess.STDOUT)
		
		if return_code != 0:
			logger.error('Preprocessing terminated with errors')
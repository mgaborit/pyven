import subprocess, os, logging

logger = logging.getLogger('global')

# pym.xml 'tool' node
class Tool(object):

	def __init__(self, node):
		self.name = node.get('name')
		self.id = node.get('id')
		self.scope = node.get('scope')
		
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
	
	def process(self):
		logger.info('Preprocessing with : ' + self.name + ':' + self.id)
		if subprocess.call(['cmake', '-H.', '-B'+self.output_path, '-G'+self.generator+''], stdout=subprocess.PIPE) != 0:
			logger.error('Preprocessing terminated with errors')
		
class MSBuildTool(Tool):

	def __init__(self, node):
		super(MSBuildTool, self).__init__(node)
		self.project_file = node.find('project-file').text
		self.configuration = node.find('configuration').text
		self.architecture = node.find('architecture').text
		
	def process(self):
		logger.info('Building with : ' + self.name + ':' + self.id)
		if subprocess.call(['msbuild.exe', self.project_file, '/property:Configuration='+self.configuration, '/property:Platform='+self.architecture], stdout=subprocess.PIPE) != 0:
			logger.error('Build terminated with errors')
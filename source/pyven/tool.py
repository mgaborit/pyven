import subprocess, os, logging, shutil, time

from pyven.exception import PyvenException

logger = logging.getLogger('global')

# pym.xml 'tool' node
class Tool(object):
	AVAILABLE_TOOLS = ['cmake', 'msbuild', 'command', 'makefile']
	AVAILABLE_SCOPES = ['preprocess', 'build']
	STATUS = ['SUCCESS', 'FAILURE']
	
	def __init__(self, node):
		self.steps = []
		self.type = node.get('type')
		if self.type is None:
			raise PyvenException('Missing tool type')
		if self.type not in Tool.AVAILABLE_TOOLS:
			raise PyvenException('Wrong tool type : ' + self.type, 'Available tools : ' + str(Tool.AVAILABLE_TOOLS))
		self.name = node.get('name')
		if self.name is None:
			raise PyvenException('Missing tool name')
		self.scope = node.get('scope')
		if self.scope is None:
			raise PyvenException('Missing tool scope')
		if self.scope not in Tool.AVAILABLE_SCOPES:
			raise PyvenException('Wrong tool scope : ' + self.scope, 'Available scopes : ' + str(Tool.AVAILABLE_SCOPES))
		
	def status(self):
		i = 0
		status = Tool.STATUS[0]
		while status == Tool.STATUS[0] and i < len(self.steps):
			if self.steps[i]['status'] == Tool.STATUS[1]:
				status = Tool.STATUS[1]
			i += 1
		return status
		
	def _report_error(self, error):
		html_str = '<div class="errorDiv">'
		html_str += '<span class="error">' + error + '</span>'
		html_str += '</div>'
		return html_str
	
	def _report_warning(self, warning):
		html_str = '<div class="warningDiv">'
		html_str += '<span class="warning">' + warning + '</span>'
		html_str += '</div>'
		return html_str
	
	def _report_informations(self, step):
		html_str += '<h2>' + self.name + '</h2>'
	
	def _report(self, nb_lines):
		html_str = ''
		i = 0
		for step in self.steps:
			html_str += self._report_informations(step)
			for error in step['errors']:
				if i < nb_lines:
					html_str += self._report_error(error)
					i += 1
			for warning in step['warnings']:
				if i < nb_lines:
					html_str += self._report_warning(warning)
					i += 1
		return html_str
	
	def report(self, nb_lines=10):
		html_str = '<div class="stepDiv">'
		html_str += self._report(nb_lines)
		html_str += '</div>'
		return html_str
	
	def _parse_logs(self, logs, step, type, error_tokens, except_tokens):
		if os.name == 'nt':
			encoding = 'windows-1252'
		else:
			encoding = 'utf-8'
		for line in [l.decode(encoding) for l in logs]:
			i = 0
			found = False
			while not found and i < len(error_tokens):
				if error_tokens[i] in line:
					step[type].append(line)
					found = True
				else:
					i += 1

	def _format_call(self):
		raise NotImplementedError
	
	def process(self):
		raise NotImplementedError
		
	def clean(self, verbose=False):
		raise NotImplementedError
		
	def factory(node):
		type = node.get('type')
		if type is None:
			raise PyvenException('Missing tool type')
		if type not in Tool.AVAILABLE_TOOLS:
			raise PyvenException('Wrong tool type : ' + type, 'Available tools : ' + str(Tool.AVAILABLE_TOOLS))
		if type == "cmake": return CMakeTool(node)
		if type == "msbuild": return MSBuildTool(node)
		if type == "command": return CommandTool(node)
		if type == "makefile": return MakefileTool(node)
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
		self.steps.append({'status' : Tool.STATUS[0], 'duration' : 0, 'warnings' : [], 'errors' : []})
	
	def _format_call(self):
		call = [self.type, '-H.', '-B'+self.output_path, '-G'+self.generator+'']
		for definition in self.definitions:
			call.append('-D'+definition)
			
		return call
	
	def _report_informations(self, step):
		html_str = '<h2>' + self.type + ' ' + self.name + '</h2>'
		html_str += '<div class="propertiesDiv">'
		html_str += '<p class="property">Generator : ' + self.generator + '</p>'
		if step['status'] == Tool.STATUS[0]:
			html_str += '<p class="property">Status : <span class="success">' + step['status'] + '</span></p>'
		elif step['status'] == Tool.STATUS[1]:
			html_str += '<p class="property">Status : <span class="failure">' + step['status'] + '</span></p>'
		html_str += '<p class="property">Duration : ' + str(step['duration']) + ' seconds</p>'
		html_str += '</div>'
		return html_str
	
	def process(self, verbose=False):
		logger.info('Preprocessing : ' + self.type + ':' + self.name)
		
		tic = time.time()
		sp = subprocess.Popen(self._format_call(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		toc = time.time()
		self.steps[0]['duration'] = round(toc - tic, 3)
		out, err = sp.communicate()
		
		if verbose:
			for line in out.splitlines():
				logger.info(line)
			for line in err.splitlines():
				logger.info(line)
		
		self._parse_logs([out], self.steps[0], 'warnings', ['Warning', 'warning'], [])
		
		if sp.returncode != 0:
			self.steps[0]['status'] = Tool.STATUS[1]
			self._parse_logs([err], self.steps[0], 'errors', ['Error', 'error'], [])
			logger.error('Preprocessing failed : ' + self.type + ':' + self.name)
		return sp.returncode == 0
	
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
		for project in node.xpath('projects/project'):
			self.steps.append({'project' : project.text, 'status' : Tool.STATUS[0], 'duration' : 0, 'warnings' : [], 'errors' : []})
		self.options = []
		for option in node.xpath('options/option'):
			self.arguments.append(option.text)
		if self.scope == 'preprocess':
			logger.warning('MSBuild will be called during preprocessing but not build')
		
	def _format_call(self, project, clean=False):
		call = ['msbuild.exe', project]
		if project.endswith('.sln'):
			call.append('/property:Configuration='+self.configuration)
			call.append('/property:Platform='+self.architecture)
			if clean:
				call.append('/t:clean')
		elif project.endswith('.dproj'):
			call.append('/p:config='+self.configuration)
			call.append('/p:platform='+self.architecture)
			if clean:
				call.append('/t:clean')
			else:
				call.append('/t:build')
		else:
			raise PyvenException('Project format not supported : ' + project, 'Supported formats : *.sln, *.dproj')
		for option in self.options:
			call.append(option)
			
		return call
	
	def _report_informations(self, step):
		html_str = '<h2>' + self.type + ' ' + self.name + ' : ' + step['project'] + '</h2>'
		html_str += '<div class="propertiesDiv">'
		html_str += '<p class="property">Configuration : ' + self.configuration + '</p>'
		html_str += '<p class="property">Platform : ' + self.architecture + '</p>'
		if step['status'] == Tool.STATUS[0]:
			html_str += '<p class="property">Status : <span class="success">' + step['status'] + '</span></p>'
		elif step['status'] == Tool.STATUS[1]:
			html_str += '<p class="property">Status : <span class="failure">' + step['status'] + '</span></p>'
		html_str += '<p class="property">Duration : ' + str(step['duration']) + ' seconds</p>'
		html_str += '</div>'
		return html_str
	
	def process(self, verbose=False):
		logger.info('Building : ' + self.type + ':' + self.name)
		ok = True
		for step in self.steps:
			project = step['project']
			tic = time.time()
			sp = subprocess.Popen(self._format_call(project), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			toc = time.time()
			self.steps[0]['duration'] = round(toc - tic, 3)
			out, err = sp.communicate()
			
			if verbose:
				for line in out.splitlines():
					logger.info(line)
				for line in err.splitlines():
					logger.info(line)

			self._parse_logs(out.splitlines(), step, 'warnings', ['Warning', 'warning', 'Avertissement', 'avertissement'], [])
				
			if sp.returncode != 0:
				step['status'] = Tool.STATUS[1]
				self._parse_logs(out.splitlines(), step, 'errors', ['Error', 'error', 'Erreur', 'erreur'], [])
				ok = False
		if not ok:
			logger.error('Build failed : ' + self.type + ':' + self.name)
		return ok
		
	def clean(self, verbose=False):
		FNULL = open(os.devnull, 'w')
		logger.info('Cleaning : ' + self.type + ':' + self.name)
		ok = True
		for step in self.steps:
			project = step['project']
			return_code = 0
			if os.path.isfile(project):
				if verbose:
					return_code = subprocess.call(self._format_call(project, clean=True))
				else:
					return_code = subprocess.call(self._format_call(project, clean=True), stdout=FNULL, stderr=subprocess.STDOUT)
			if return_code != 0:
				ok = False
		if not ok:
			logger.error('Clean failed : ' + self.type + ':' + self.name)
		return ok
			
class CommandTool(Tool):

	def __init__(self, node):
		super(CommandTool, self).__init__(node)
		programs = node.xpath('program')
		if len(programs) < 1:
			raise PyvenException('Missing program')
		if len(programs) > 1:
			raise PyvenException('Too many programs specified')
		self.program = programs[0]
		self.options = []
		for option in node.xpath('options/option'):
			self.options.append(option.text)
		self.arguments = []
		for argument in node.xpath('arguments/argument'):
			self.arguments.append(argument.text)
		
	def _format_call(self):
		call = [self.program]
		for option in self.options:
			call.append(option)
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
					
class MakefileTool(Tool):

	def __init__(self, node):
		super(MakefileTool, self).__init__(node)
		workspaces = node.xpath('workspace')
		if len(workspaces) < 1:
			raise PyvenException('Missing Makefile directory')
		if len(workspaces) > 1:
			raise PyvenException('Too many Makefile directories specified, only one needed')
		self.workspace = workspaces[0].text
		self.options = []
		for option in node.xpath('options/option'):
			self.options.append(option.text)
		self.rules = []
		for rule in node.xpath('rules/rule'):
			self.rules.append(rule.text)
		if self.scope == 'preprocess':
			logger.warning('Makefile will be called during preprocessing but not build')
		
	def _format_call(self, clean=False):
		call = ['make']
		if clean:
			call.append('clean')
		else:
			for option in self.options:
				call.append(option)
			for rule in self.rules:
				call.append(rule)
			
		return call
	
	def process(self, verbose=False):
		FNULL = open(os.devnull, 'w')
		cwd = os.getcwd()
		logger.info('Entering test directory : ' + self.workspace)
		if os.path.isdir(self.workspace):
			os.chdir(self.workspace)
			logger.info('Building : ' + self.type + ':' + self.name)
			if verbose:
				return_code = subprocess.call(self._format_call())
			else:
				return_code = subprocess.call(self._format_call(), stdout=FNULL, stderr=subprocess.STDOUT)
			os.chdir(cwd)
			if return_code != 0:
				logger.error('Build failed : ' + self.type + ':' + self.name)
				return False
			return True
		logger.error('Unknown directory : ' + self.workspace)
		return False
		
	def clean(self, verbose=False):
		FNULL = open(os.devnull, 'w')
		cwd = os.getcwd()
		logger.info('Entering test directory : ' + self.workspace)
		if os.path.isdir(self.workspace):
			os.chdir(self.workspace)
			logger.info('Cleaning : ' + self.type + ':' + self.name)
			if verbose:
				return_code = subprocess.call(self._format_call(clean=True))
			else:
				return_code = subprocess.call(self._format_call(clean=True), stdout=FNULL, stderr=subprocess.STDOUT)
			if return_code != 0:
				logger.error('Clean failed : ' + self.type + ':' + self.name)
				return False
			return True
		logger.error('Unknown directory : ' + self.workspace)
		return False
		
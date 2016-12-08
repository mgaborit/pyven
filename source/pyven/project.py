import logging, os, shutil, time
from lxml import etree

from pyven.exception import PyvenException

from pyven.report import Report

from pyven.artifact import Artifact
from pyven.package import Package
from pyven.tool import Tool
from pyven.test import Test
from pyven.repository import Repository

logger = logging.getLogger('global')

class Project:
	POSSIBLE_STEPS = ['configure', 'build', 'test', 'package', 'verify', 'install', 'deploy', 'deliver', 'clean', 'retrieve']
	WORKSPACE = 'pvn_workspace'
	LOCAL_REPO_NAME = 'local'
	
	if os.name == 'nt':
		LOCAL_REPO = os.path.join(os.environ.get('USERPROFILE'), 'pvn_repo')
	elif os.name == 'posix':
		LOCAL_REPO = os.path.join(os.environ.get('HOME'), 'pvn_repo')

	def __init__(self, version, verbose=False):
		logger.info('Initializing Pyven project')
		
		self.version = version
		self.verbose = verbose
		if os.name == 'nt':
			self.platform = 'windows'
		elif os.name == 'posix':
			self.platform = 'linux'
		else:
			raise PyvenException('Unsupported platform')
		logger.info('Project set for '+self.platform+' platform')
		
		self.artifacts = {}
		self.packages = {}
		self.repositories = {}
		self.repositories[Project.LOCAL_REPO_NAME] = Repository._factory(Project.LOCAL_REPO_NAME, 'file', Project.LOCAL_REPO)
		logger.info('Local repository set at : ' + self.repositories[Project.LOCAL_REPO_NAME].url)
		self.tools = {"preprocessors" : [], "builders" : []}
		self.unit_tests = []
		self.integration_tests = []

	def tic():
		return time.time()
	tic = staticmethod(tic)
		
	def toc():
		return Project.tic()
	toc = staticmethod(toc)
		
	def _extract_artifacts(self, tree):
		for node in tree.xpath('/pyven/platform[@name="'+self.platform+'"]/artifacts/artifact'):
			artifact = Artifact(node)
			if artifact.format_name() in self.artifacts.keys():
				raise PyvenException('Artifact already added : ' + artifact.format_name())
			else:
				if artifact.file is None:
					if artifact.to_retrieve:
						self.repositories[artifact.repo].retrieve(artifact, Project.WORKSPACE)
						logger.info('Retrieved artifact from ' + self.repositories[artifact.repo].name + ' repository : ' + artifact.format_name())
				self.artifacts[artifact.format_name()] = artifact
				logger.info('Added artifact : ' + artifact.format_name())
	
	def _extract_packages(self, tree):
		for node in tree.xpath('/pyven/platform[@name="'+self.platform+'"]/packages/package'):
			package = Package(node)
			if package.format_name() in self.packages.keys():
				raise PyvenException('Package already added : ' + package.format_name())
			else:
				if package.to_retrieve:
					self.repositories[package.repo].retrieve(package, Project.WORKSPACE)
					logger.info('Retrieved package from ' + self.repositories[package.repo].name + ' repository : ' + package.format_name())
				else:
					for item in node.xpath('item'):
						if item.text in self.artifacts.keys():
							artifact = self.artifacts[item.text]
							package.items.append(artifact)
							logger.info('Package ' + package.format_name() + ' : Added artifact ' + artifact.format_name())
						else:
							raise PyvenException('Package ' + package.format_name() + ' : Artifact not found : ' + item.text)
				self.packages[package.format_name()] = package
				logger.info('Added package : ' + package.format_name())
	
	def _extract_tools(self, tree):
		for node in tree.xpath('/pyven/platform[@name="'+self.platform+'"]/build/tools/tool[@scope="preprocess"]'):
			preprocessor = Tool.factory(node)
			self.tools['preprocessors'].append(preprocessor)
			logger.info('Added preprocessor : ' + preprocessor.type + ':' + preprocessor.name)
		for node in tree.xpath('/pyven/platform[@name="'+self.platform+'"]/build/tools/tool[@scope="build"]'):
			builder = Tool.factory(node)
			self.tools['builders'].append(builder)
			logger.info('Added builder : ' + builder.type + ':' + builder.name)
	
	def _extract_tests(self, tree):
		for node in tree.xpath('/pyven/platform[@name="'+self.platform+'"]/tests/test'):
			test = Test.factory(node)
			if test.type == 'unit':
				self.unit_tests.append(test)
				logger.info('Added unit test : ' + os.path.join(test.path, test.filename))
			elif test.type == 'integration':
				self.integration_tests.append(test)
				logger.info('Added integration test : ' + os.path.join(test.path, test.filename))
			else:
				raise PyvenException('Wrong test type : ' + test.name, 'Available types : ' + str(Test.AVAILABLE_TYPES))
	
	def _extract_repositories(self, tree):
		for node in tree.xpath('/pyven/platform[@name="'+self.platform+'"]/repositories/repository'):
			repository = Repository.factory(node)
			if repository.name in self.repositories.keys():
				logger.error('Repository already added : ' + repository.name + ' : ' + repository.url)
			else:
				self.repositories[repository.name] = repository
				logger.info('Added repository : ' + repository.name + ' : ' + repository.url)
	
	def _step(function, arg=None):
		def __intern(self=None, arg=None):
			logger.info('===================================')
			try:
				tic = Project.tic()
				function(self, arg)
				toc = Project.toc()
				logger.info('Step time : ' + str(round(toc - tic, 3)) + ' seconds')
			except PyvenException as e:
				for msg in e.args:
					logger.error(msg)
				return False
			return True
		return __intern
		
	@_step
	def configure(self, arg=None):
		logger.info('STEP CONFIGURE : STARTING')
		if not os.path.isdir(Project.WORKSPACE):
			os.makedirs(Project.WORKSPACE)
		if not os.path.isdir(os.path.join(Project.WORKSPACE, 'packages')):
			os.makedirs(os.path.join(Project.WORKSPACE, 'packages'))
		if not os.path.isdir(os.path.join(Project.WORKSPACE, 'artifacts')):
			os.makedirs(os.path.join(Project.WORKSPACE, 'artifacts'))
		logger.info('Created Pyven workspace')
		logger.info('Starting pym.xml parsing')
		tree = etree.parse('pym.xml')
		doc_element = tree.getroot()
		if doc_element is None or doc_element.tag == "name":
			raise PyvenException('Missing "pyven" markup')
		expected_pyven_version = doc_element.get('version')
		if expected_pyven_version is None:
			raise PyvenException('Missing pyven version information')
		logger.info('Expected pyven version : ' + expected_pyven_version)
		if expected_pyven_version != self.version:
			raise PyvenException('Wrong pyven version', 'Expected version : Pyven ' + expected_pyven_version, 'Version in use : ' + self.version)
		logger.info('PYM parsing successful')
		self._extract_repositories(tree)
		self._extract_artifacts(tree)
		self._extract_packages(tree)
		self._extract_tools(tree)
		self._extract_tests(tree)
		logger.info('STEP CONFIGURE : SUCCESSFUL')
		
	@_step	
	def build(self, arg=None):
		logger.info('STEP BUILD : STARTING')
		logger.info('Starting preprocessing')
		preprocess_ok = True
		for tool in self.tools['preprocessors']:
			tic = Project.tic()
			if not tool.process(self.verbose):
				preprocess_ok = False
			else:
				toc = Project.toc()
				logger.info('Time for ' + tool.type + ':' + tool.name + ' : ' + str(round(toc - tic, 3)) + ' seconds')
		if not preprocess_ok:
			self.write_report()
			raise PyvenException('Preprocessing errors found')
		logger.info('Preprocessing completed')
		logger.info('Starting build')
		build_ok = True
		for tool in self.tools['builders']:
			tic = Project.tic()
			if not tool.process(self.verbose):
				build_ok = False
			else:
				toc = Project.toc()
				logger.info('Time for ' + tool.type + ':' + tool.name + ' : ' + str(round(toc - tic, 3)) + ' seconds')
		if not build_ok:
			self.write_report()
			raise PyvenException('Build errors found')
		logger.info('build completed')
		artifacts_ok = True
		for artifact in [a for a in self.artifacts.values() if not a.to_retrieve]:
			if not os.path.isfile(artifact.file):
				logger.error('Artifact not found : ' + artifact.format_name())
				artifacts_ok = False
		if not artifacts_ok:
			raise PyvenException('Artifacts missing')
		for artifact in [a for a in self.artifacts.values() if not a.to_retrieve]:
			if not os.path.isdir(artifact.location(Project.WORKSPACE)):
				os.makedirs(artifact.location(Project.WORKSPACE))
			shutil.copy(artifact.file, artifact.location(Project.WORKSPACE))
		logger.info('STEP BUILD : SUCCESSFUL')
		
	@_step
	def test(self, arg=None):
		logger.info('STEP TEST : STARTING')
		if len(self.unit_tests) == 0:
			logger.warning('No unit tests found')
		else:
			tests_ok = True
			for test in self.unit_tests:
				tic = Project.tic()
				if not test.run(self.report, self.verbose):
					tests_ok = False
				else:
					toc = Project.toc()
					logger.info('Time for test ' + test.filename + ' : ' + str(round(toc - tic, 3)) + ' seconds')
			if not tests_ok:
				raise PyvenException('Test failures found')
		logger.info('STEP TEST : SUCCESSFUL')

	@_step
	def package(self, arg=None):
		logger.info('STEP PACKAGE : STARTING')
		for package in self.packages.values():
			package.pack(Project.WORKSPACE)
		logger.info('STEP PACKAGE : SUCCESSFUL')

	@_step
	def verify(self, arg=None):
		logger.info('STEP VERIFY : STARTING')
		if len(self.integration_tests) == 0:
			logger.warning('No integration tests found')
		else:
			tests_ok = True
			for test in self.integration_tests:
				tic = Project.tic()
				if not test.run(self.verbose, Project.WORKSPACE, self.packages):
					tests_ok = False
				else:
					toc = Project.toc()
					logger.info('Time for test ' + test.filename + ' : ' + str(round(toc - tic, 3)) + ' seconds')
			if not tests_ok:
				self.write_report()
				raise PyvenException('Test failures found')
		logger.info('STEP VERIFY : SUCCESSFUL')
		
	@_step
	def install(self, arg=None):
		logger.info('STEP INSTALL : STARTING')
		for artifact in [a for a in self.artifacts.values() if a.repo is None]:
			self.repositories[Project.LOCAL_REPO_NAME].publish(artifact, Project.WORKSPACE)
			logger.info('Published artifact to ' + Project.LOCAL_REPO_NAME + ' repository : ' + artifact.format_name())
		for package in [p for p in self.packages.values() if not p.to_retrieve]:
			self.repositories[Project.LOCAL_REPO_NAME].publish(package, Project.WORKSPACE)
			logger.info('Published package to ' + Project.LOCAL_REPO_NAME + ' repository : ' + package.format_name())
		logger.info('STEP INSTALL : SUCCESSFUL')
		
	@_step
	def deploy(self, repo=None):
		logger.info('STEP DEPLOY : STARTING')
		for key in [k for k in self.repositories.keys() if k != Project.LOCAL_REPO_NAME]:
			for artifact in [a for a in self.artifacts.values() if not a.to_retrieve]:
				self.repositories[key].publish(artifact, Project.WORKSPACE)
				logger.info('Published artifact to ' + key + ' repository : ' + artifact.format_name())
			for package in [p for p in self.packages.values() if not p.to_retrieve]:
				self.repositories[key].publish(package, Project.WORKSPACE)
				logger.info('Published package to ' + key + ' repository : ' + package.format_name())
		logger.info('STEP DEPLOY : SUCCESSFUL')
		
	@_step
	def deliver(self, path):
		logger.info('STEP DELIVER : STARTING')
		logger.info('Delivering to directory ' + path)
		for package in [p for p in self.packages.values() if p.repo is None]:
			package.unpack(path, Project.LOCAL_REPO, flatten=False)
			logger.info('Delivered package : ' + package.format_name())
		logger.info('STEP DELIVER : SUCCESSFUL')
		
	@_step
	def clean(self, verbose=False):
		logger.info('STEP CLEAN : STARTING')
		build_ok = True
		for tool in self.tools['builders']:
			if not tool.clean(self.verbose):
				build_ok = False
		preprocess_ok = True
		for tool in self.tools['preprocessors']:
			if not tool.clean(self.verbose):
				preprocess_ok = False
		if not preprocess_ok or not build_ok:
			raise PyvenException('Cleaning errors found')
		logger.info('STEP CLEAN : SUCCESSFUL')
	
	@_step
	def retrieve(self, arg=None):
		logger.info('STEP RETRIEVE : STARTING')
		for artifact in [a for a in self.artifacts.values() if a.to_retrieve]:
			for package in self.packages.values():
				for item in [i for i in package.items if i.to_retrieve]:
					if artifact.format_name() == item.format_name():
						for built_artifact in [a for a in self.artifacts.values() if not a.to_retrieve]:
							dir = os.path.dirname(built_artifact.file)
							if not os.path.isdir(dir):
								os.makedirs(dir)
							shutil.copy(os.path.join(artifact.location(Project.WORKSPACE), artifact.basename()), os.path.join(dir, artifact.basename()))
		logger.info('STEP RETRIEVE : SUCCESSFUL')
	
	def write_report(self):
		i = 0
		build_ok = True
		while build_ok and i < len(self.tools['preprocessors']):
			if self.tools['preprocessors'][i].status() == 'FAILURE':
				build_ok = False
			i += 1
		i = 0
		while build_ok and i < len(self.tools['builders']):
			if self.tools['builders'][i].status() == 'FAILURE':
				build_ok = False
			i += 1
			
		i = 0
		unit_ok = True
		if build_ok:
			while unit_ok and i < len(self.unit_tests):
				if self.unit_tests[i].status == 'FAILURE':
					unit_ok = False
				i += 1
		
		i = 0
		integration_ok = True
		if build_ok and unit_ok:
			while integration_ok and i < len(self.integration_tests):
				if self.integration_tests[i].status == 'FAILURE':
					integration_ok = False
				i += 1
				
		if build_ok and unit_ok and integration_ok:
			status = 'SUCCESS'
		else:
			status = 'FAILURE'
		report = Report(status)
		if build_ok and unit_ok:
			report.prepare_summary(self.tools['preprocessors'], self.tools['builders'], self.unit_tests, self.integration_tests)
		elif build_ok:
			report.prepare_summary(self.tools['preprocessors'], self.tools['builders'], self.unit_tests)
		else:
			report.prepare_summary(self.tools['preprocessors'], self.tools['builders'])
		for tool in self.tools['preprocessors']:
			report.steps.append(tool.report())
		for tool in self.tools['builders']:
			report.steps.append(tool.report())
		if build_ok:
			for test in self.unit_tests:
				report.steps.append(test.report())
		if build_ok and unit_ok:
			for test in self.integration_tests:
				report.steps.append(test.report())
		report.write(Project.WORKSPACE)
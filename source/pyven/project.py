import logging, os, shutil
from lxml import etree

from artifact import Artifact
from package import Package
from tool import Tool
from test import Test
from repository import Repository

logger = logging.getLogger('global')

class Project:
	WORKSPACE = 'pyven_workspace'
	LOCAL_REPO_NAME = 'local'
	if os.name == 'nt':
		LOCAL_REPO = os.path.join(os.environ.get('USERPROFILE'), 'pyven_local_repo')
	elif os.name == 'posix':
		LOCAL_REPO = os.path.join(os.environ.get('HOME'), 'pyven_local_repo')

	def __init__(self, verbose=False):
		logger.info('Initializing Pyven project')
		
		self.verbose = verbose
		if os.name == 'nt':
			self.platform = 'windows'
		elif os.name == 'posix':
			self.platform = 'linux'
		logger.info('Project set for '+self.platform+' platform')
		
		self.artifacts = {}
		self.packages = {}
		self.repositories = {}
		self.repositories[Project.LOCAL_REPO_NAME] = Repository._factory(Project.LOCAL_REPO_NAME, 'file', Project.LOCAL_REPO)
		logger.info('Local repository set at : ' + self.repositories[Project.LOCAL_REPO_NAME].url)
		self.tools = {"preprocessors" : [], "builders" : []}
		self.unit_tests = []
		self.integration_tests = []

	def clean(self):
		print 'clean'
	
	def _extract_artifacts(self, tree):
		for node in tree.xpath('/pyven/platform[@id="'+self.platform+'"]/artifacts/artifact'):
			artifact = Artifact(node)
			if artifact.format_name() in self.artifacts.keys():
				logger.error('Artifact already added : ' + artifact.format_name())
			else:
				if artifact.file is None:
					if artifact.repo is None:
						logger.info('Impossible to retrieve artifact : ' + artifact.format_name())
					else:
						self.repositories[artifact.repo].retrieve(artifact, Project.WORKSPACE)
						logger.info('Retrieved artifact from ' + self.repositories[artifact.repo].id + ' repository : ' + artifact.format_name())
				self.artifacts[artifact.format_name()] = artifact
				logger.info('Added artifact : ' + artifact.format_name())
	
	def _extract_tools(self, tree):
		for node in tree.xpath('/pyven/platform[@id="'+self.platform+'"]/build/tools/tool[@scope="preprocess"]'):
			preprocessor = Tool.factory(node)
			self.tools['preprocessors'].append(preprocessor)
			logger.info('Added preprocessor : ' + preprocessor.name + ':' + preprocessor.id)
		for node in tree.xpath('/pyven/platform[@id="'+self.platform+'"]/build/tools/tool[@scope="build"]'):
			builder = Tool.factory(node)
			self.tools['builders'].append(builder)
			logger.info('Added builder : ' + builder.name + ':' + builder.id)
	
	def _extract_tests(self, tree):
		for node in tree.xpath('/pyven/platform[@id="'+self.platform+'"]/tests/test[@type="unit"]'):
			test = Test(node)
			self.unit_tests.append(test)
			logger.info('Added unit test : ' + os.path.join(test.path, test.filename))
		for node in tree.xpath('/pyven/platform[@id="'+self.platform+'"]/tests/test[@type="integration"]'):
			test = Test(node)
			self.integration_tests.append(test)
			logger.info('Added unit test : ' + os.path.join(test.path, test.filename))
	
	def _extract_packages(self, tree):
		for node in tree.xpath('/pyven/platform[@id="'+self.platform+'"]/packages/package'):
			package = Package(node)
			if package.format_name() in self.packages.keys():
				logger.error('Package already added : ' + package.format_name())
			else:
				for item in node.xpath('item'):
					if item.text in self.artifacts.keys():
						artifact = self.artifacts[item.text]
						package.items.append(artifact)
						logger.info('Added artifact ' + artifact.format_name() + ' to package ' + package.format_name())
					else:
						logger.error('Artifact not found : ' + item.text)
				self.packages[package.format_name()] = package
				logger.info('Added package : ' + package.format_name())
	
	def _extract_repositories(self, tree):
		for node in tree.xpath('/pyven/platform[@id="'+self.platform+'"]/repositories/repository'):
			repository = Repository.factory(node)
			if repository.id in self.repositories.keys():
				logger.error('Repository already added : ' + repository.id + ' : ' + repository.url)
			else:
				self.repositories[repository.id] = repository
				logger.info('Added repository : ' + repository.id + ' : ' + repository.url)
	
	def configure(self):
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
		logger.info('PYM parsing successful')
		self._extract_repositories(tree)
		self._extract_artifacts(tree)
		self._extract_packages(tree)
		self._extract_tools(tree)
		self._extract_tests(tree)
		logger.info('STEP CONFIGURE : COMPLETED')

			
	def build(self):
		logger.info('STEP BUILD : STARTING')
		logger.info('Starting preprocessing')
		for tool in self.tools['preprocessors']:
			tool.process(self.verbose)
		logger.info('Preprocessing completed')
		logger.info('Starting build')
		for tool in self.tools['builders']:
			tool.process(self.verbose)
		logger.info('build completed')
		for artifact in [a for a in self.artifacts.values() if a.repo is None]:
			if os.path.isfile(artifact.file):
				if not os.path.isdir(artifact.workspace_location(Project.WORKSPACE)):
					os.makedirs(artifact.workspace_location(Project.WORKSPACE))
				shutil.copy(artifact.file, artifact.workspace_location(Project.WORKSPACE))
			else:
				logger.error('Missing artifact : ' + artifact.format_name())
		logger.info('STEP BUILD : COMPLETED')
		
		
	def test(self):
		logger.info('STEP TEST : STARTING')
		if len(self.unit_tests) == 0:
			logger.warning('No unit tests found')
		else:
			for test in self.unit_tests:
				test.run(self.verbose)
		logger.info('STEP TEST : COMPLETED')
		
		
	def package(self):
		logger.info('STEP PACKAGE : STARTING')
		for package in self.packages.values():
			package.pack(Project.WORKSPACE)
		logger.info('STEP PACKAGE : COMPLETED')
		
		
	def verify(self):
		logger.info('STEP VERIFY : STARTING')
		if len(self.integration_tests) == 0:
			logger.warning('No integration tests found')
		else:
			for test in self.integration_tests:
				test.run(self.verbose)
		logger.info('STEP VERIFY : COMPLETED')
		
		
	def install(self, unpack=False):
		logger.info('STEP INSTALL : STARTING')
		for artifact in [a for a in self.artifacts.values() if a.repo is None]:
			self.repositories[Project.LOCAL_REPO_NAME].publish(artifact, Project.WORKSPACE)
			logger.info('Published artifact to ' + Project.LOCAL_REPO_NAME + ' repository : ' + artifact.format_name())
		for package in self.packages.values():
			self.repositories[Project.LOCAL_REPO_NAME].publish(package, Project.WORKSPACE)
			logger.info('Published package to ' + Project.LOCAL_REPO_NAME + ' repository : ' + artifact.format_name())
		logger.info('STEP INSTALL : COMPLETED')
		
		
	def deploy(self, repo=None, unpack=False):
		logger.info('STEP DEPLOY : STARTING')
		for key in [k for k in self.repositories.keys() if k != Project.LOCAL_REPO_NAME]:
			for artifact in [a for a in self.artifacts.values() if a.repo is None]:
				self.repositories[key].publish(artifact, Project.WORKSPACE)
				logger.info('Published artifact to ' + key + ' repository : ' + artifact.format_name())
			for package in self.packages.values():
				self.repositories[key].publish(package, Project.WORKSPACE)
				logger.info('Published package to ' + key + ' repository : ' + artifact.format_name())
		logger.info('STEP DEPLOY : COMPLETED')

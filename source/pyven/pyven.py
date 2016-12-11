import logging, os, shutil, time
from lxml import etree

import pyven.constants
from pyven.exceptions.exception import PyvenException

from pyven.items.artifact import Artifact
from pyven.items.package import Package

from pyven.repositories.directory import DirectoryRepo

from pyven.processing.tools.tool import Tool
from pyven.processing.tests.test import Test

from pyven.utils.pym_parser import PymParser
from pyven.utils.factory import Factory

logger = logging.getLogger('global')

class Pyven:
	WORKSPACE = Factory.create_repo('workspace', 'workspace', 'pvn_workspace')
	if not os.path.isdir(WORKSPACE.url):
		os.makedirs(WORKSPACE.url)
		
	if pyven.constants.PLATFORM == 'windows':
		LOCAL_REPO = Factory.create_repo('local', 'file', os.path.join(os.environ.get('USERPROFILE'), 'pvn_repo'))
	elif pyven.constants.PLATFORM == 'linux':
		LOCAL_REPO = Factory.create_repo('local', 'file', os.path.join(os.environ.get('HOME'), 'pvn_repo'))
	if not os.path.isdir(LOCAL_REPO.url):
		os.makedirs(LOCAL_REPO.url)

	def __init__(self, step, version, verbose=False, pym='pym.xml'):
		logger.info('Initializing Pyven project')
		logger.info('Pyven set for '+pyven.constants.PLATFORM+' platform')
		logger.info('Workspace set at : ' + Pyven.WORKSPACE.url)
		logger.info('Local repository set at : ' + Pyven.LOCAL_REPO.url)
		
		self.step = step
		self.verbose = verbose
		self.pym = pym
		self.parser = PymParser(self.pym)
		self.objects = {'preprocessors': [], 'builders': [], 'unit_tests': [], 'integration_tests': []}
		
	def reportables(self):
		reportables = []
		if self.step in ['verify', 'install', 'deploy', 'deliver']:
			reportables.extend(self.objects['preprocessors'])
			reportables.extend(self.objects['builders'])
			reportables.extend(self.objects['unit_tests'])
			reportables.extend(self.objects['integration_tests'])
		elif self.step in ['test', 'package']:
			reportables.extend(self.objects['preprocessors'])
			reportables.extend(self.objects['builders'])
			reportables.extend(self.objects['unit_tests'])
		elif self.step in ['build']:
			reportables.extend(self.objects['preprocessors'])
			reportables.extend(self.objects['builders'])
		return reportables
	
	@staticmethod
	def _log_step_delimiter():
		logger.info('===================================')
	
	def _step(function, arg=None):
		def __intern(self=None, arg=None):
			try:
				tic = time.time()
				function(self, arg)
				toc = time.time()
				logger.info('Step time : ' + str(round(toc - tic, 3)) + ' seconds')
			except PyvenException as e:
				for msg in e.args:
					logger.error(msg)
				logger.error('STEP FAILED')
				return False
			return True
		return __intern
		
# ============================================================================================================		

	@staticmethod
	def _check_repositories(repositories):
		checked = {}
		for repo in repositories:
			if repo.name == Pyven.WORKSPACE.name or repo.name == Pyven.LOCAL_REPO.name:
				logger.error('Repository name reserved --> ' + repo.name + ' : ' + repo.url)
			else:
				if repo.name in checked.keys():
					logger.error('Repository already added --> ' + repo.name + ' : ' + repo.url)
				else:
					if repo.is_available():
						checked[repo.name] = repo
						logger.info('Repository added --> ' + repo.name + ' : ' + repo.url)
					else:
						logger.warning('Repository not accessible --> ' + repo.name + ' : ' + repo.url)
		return checked
		
	@staticmethod
	def _check_artifacts(artifacts):
		checked = {}
		for artifact in artifacts:
			if artifact.format_name() in checked.keys():
				logger.error('Artifact already added --> ' + artifact.format_name())
			else:
				checked[artifact.format_name()] = artifact
				logger.info('Artifact added --> ' + artifact.format_name())
		return checked
		
	@staticmethod
	def _check_packages(packages, artifacts):
		checked = {}
		for package in packages:
			if package['package'].format_name() in checked.keys():
				logger.error('Package already added --> ' + package.format_name())
			else:
				for item in package['items']:
					if item not in artifacts.keys():
						logger.error('Package ' + package['package'].format_name() + ' : Artifact not declared --> ' + item)
					else:
						package['package'].items.append(artifacts[item])
						logger.info('Package ' + package['package'].format_name() + ' : Artifact added --> ' + item)
				checked[package['package'].format_name()] = package['package']
				logger.info('Package added --> ' + package['package'].format_name())
		return checked
		
	@staticmethod
	def _check_preprocessors(preprocessors):
		checked = []
		for preprocessor in preprocessors:
			checked.append(preprocessor)
			logger.info('Preprocessor added --> ' + preprocessor.type + ':' + preprocessor.name)
		return checked
		
	@staticmethod
	def _check_builders(builders):
		checked = []
		for builder in builders:
			checked.append(builder)
			logger.info('Builder added --> ' + builder.type + ':' + builder.name)
		return checked
		
	@staticmethod
	def _check_unit_tests(unit_tests):
		checked = []
		for unit_test in unit_tests:
			checked.append(unit_test)
			logger.info('Unit test added --> ' + os.path.join(unit_test.path, unit_test.filename))
		return checked
		
	@staticmethod
	def _check_integration_tests(integration_tests, packages):
		checked = []
		for integration_test in integration_tests:
			if integration_test['package'] not in packages.keys():
				logger.error('Integration test ' + os.path.join(integration_test.path, integration_test.filename)\
							+ ' : Package not declared --> ' + integration_test['package'])
			else:
				integration_test['integration_test'].package = packages[integration_test['package']]
				logger.info('Integration test ' + os.path.join(integration_test['integration_test'].path, integration_test['integration_test'].filename)\
							+ ' : Package added --> ' + integration_test['package'])
			checked.append(integration_test['integration_test'])
			logger.info('Integration test added --> ' + os.path.join(integration_test['integration_test'].path, integration_test['integration_test'].filename))
		return checked
		
	@_step
	def configure(self, arg=None):
		Pyven._log_step_delimiter()
		logger.info('STEP CONFIGURE : STARTING')
		if Pyven.WORKSPACE.is_available():
			logger.info('Created Pyven workspace')
		else:
			raise PyvenException('Could not create workspace')
		self.objects = self.parser.parse()
		self.objects['repositories'] = self._check_repositories(self.objects['repositories'])
		self.objects['artifacts'] = self._check_artifacts(self.objects['artifacts'])
		self.objects['packages'] = self._check_packages(self.objects['packages'], self.objects['artifacts'])
		self.objects['preprocessors'] = self._check_preprocessors(self.objects['preprocessors'])
		self.objects['builders'] = self._check_builders(self.objects['builders'])
		self.objects['unit_tests'] = self._check_unit_tests(self.objects['unit_tests'])
		self.objects['integration_tests'] = self._check_integration_tests(self.objects['integration_tests'], self.objects['packages'])
		logger.info('STEP CONFIGURE : SUCCESSFUL')
	
# ============================================================================================================		

	def _build(self, scope):
		if scope == 'preprocessors':
			sub_step = ('preprocessing', 'Preprocessing')
		elif scope == 'builders':
			sub_step = ('build', 'Build')
		
		logger.info('Starting ' + sub_step[0])
		ok = True
		for tool in self.objects[scope]:
			tic = time.time()
			if not tool.process(self.verbose):
				ok = False
			else:
				toc = time.time()
				logger.info('Time for ' + tool.type + ':' + tool.name + ' : ' + str(round(toc - tic, 3)) + ' seconds')
		if not ok:
			raise PyvenException(sub_step[1] + ' errors found')
		logger.info(sub_step[1] + ' completed')
	
	@_step	
	def build(self, arg=None):
		self.configure()
	
		Pyven._log_step_delimiter()
		logger.info('STEP BUILD : STARTING')
		self._build('preprocessors')
		self._build('builders')
		ok = True
		for artifact in [a for a in self.objects['artifacts'].values() if not a.to_retrieve]:
			if not os.path.isfile(artifact.file):
				logger.error('Artifact not found : ' + artifact.format_name())
				ok = False
		if not ok:
			raise PyvenException('Artifacts missing')
		for artifact in [a for a in self.objects['artifacts'].values() if not a.to_retrieve]:
			Pyven.WORKSPACE.publish(artifact, artifact.file)
		logger.info('STEP BUILD : SUCCESSFUL')
		
# ============================================================================================================		

	@staticmethod
	def _test(tests, verbose=False):
		ok = True
		for test in tests:
			tic = time.time()
			if not test.process(verbose, Pyven.WORKSPACE):
				ok = False
			else:
				toc = time.time()
				logger.info('Time for test ' + test.filename + ' : ' + str(round(toc - tic, 3)) + ' seconds')
		return ok

	@_step
	def test(self, arg=None):
		self.build()
		
		Pyven._log_step_delimiter()
		logger.info('STEP TEST : STARTING')
		if len(self.objects['unit_tests']) == 0:
			logger.warning('No unit tests found')
		else:
			if not Pyven._test(self.objects['unit_tests'], self.verbose):
				raise PyvenException('Unit test failures found')
		logger.info('STEP TEST : SUCCESSFUL')

# ============================================================================================================		

	@_step
	def package(self, arg=None):
		self.test()
		
		Pyven._log_step_delimiter()
		logger.info('STEP PACKAGE : STARTING')
		ok = True
		for package in [p for p in self.objects['packages'].values() if not p.to_retrieve]:
			package_ok = True
			for artifact in [a for a in package.items if a.to_retrieve]:
				if self.objects['repositories'][artifact.repo].is_available():
					self.objects['repositories'][artifact.repo].retrieve(artifact, Pyven.WORKSPACE)
				else:
					logger.error('Repository not accessible --> ' + self.objects['repositories'][artifact.repo].name + ' : ' + self.objects['repositories'][artifact.repo].url,\
								'Unable to retrieve artifact --> ' + artifact.format_name(),\
								'Unable to build package --> ' + package.format_name())
					package_ok = False
					ok = False
			if package_ok:
				if not package.pack(Pyven.WORKSPACE):
					ok = False
		if not ok:
			raise PyvenException('Some packages were not built')
		logger.info('STEP PACKAGE : SUCCESSFUL')

# ============================================================================================================		

	@_step
	def verify(self, arg=None):
		self.package()
		
		Pyven._log_step_delimiter()
		logger.info('STEP VERIFY : STARTING')
		if len(self.objects['integration_tests']) == 0:
			logger.warning('No integration tests found')
		else:
			if not Pyven._test(self.objects['integration_tests'], self.verbose):
				raise PyvenException('Integration test failures found')
		logger.info('STEP VERIFY : SUCCESSFUL')
		
# ============================================================================================================		

	@_step
	def install(self, arg=None):
		self.verify()
		
		Pyven._log_step_delimiter()
		logger.info('STEP INSTALL : STARTING')
		for artifact in [a for a in self.objects['artifacts'].values() if not a.to_retrieve]:
			self.LOCAL_REPO.publish(artifact, Pyven.WORKSPACE)
			logger.info('Published artifact to ' + Pyven.LOCAL_REPO.name + ' repository : ' + artifact.format_name())
		for package in [p for p in self.objects['packages'].values() if not p.to_retrieve]:
			self.LOCAL_REPO.publish(package, Pyven.WORKSPACE)
			logger.info('Published package to ' + Pyven.LOCAL_REPO.name + ' repository : ' + artifact.format_name())
		logger.info('STEP INSTALL : SUCCESSFUL')
		
# ============================================================================================================		

	@_step
	def deploy(self, repo=None):
		self.verify()
		
		Pyven._log_step_delimiter()
		logger.info('STEP DEPLOY : STARTING')
		for repo in self.objects['repositories'].values():
			for artifact in [a for a in self.objects['artifacts'].values() if not a.to_retrieve]:
				repo.publish(artifact, Pyven.WORKSPACE)
				logger.info('Published artifact to ' + repo.name + ' repository : ' + artifact.format_name())
			for package in [p for p in self.objects['packages'].values() if not p.to_retrieve]:
				repo.publish(package, Pyven.WORKSPACE)
				logger.info('Published package to ' + repo.name + ' repository : ' + package.format_name())
		logger.info('STEP DEPLOY : SUCCESSFUL')
		
# ============================================================================================================		

	@_step
	def deliver(self, path):
		self.install()
		
		Pyven._log_step_delimiter()
		logger.info('STEP DELIVER : STARTING')
		logger.info('Delivering to directory ' + path)
		for package in self.objects['packages'].values():
			package.unpack(path, Pyven.LOCAL_REPO, flatten=False)
			logger.info('Delivered package : ' + package.format_name())
		logger.info('STEP DELIVER : SUCCESSFUL')
		
# ============================================================================================================		

	@_step
	def clean(self, verbose=False):
		self.configure()
		
		Pyven._log_step_delimiter()
		logger.info('STEP CLEAN : STARTING')
		build_ok = True
		for tool in self.objects['builders']:
			if not tool.clean(self.verbose):
				build_ok = False
		preprocess_ok = True
		for tool in self.objects['preprocessors']:
			if not tool.clean(self.verbose):
				preprocess_ok = False
		if not preprocess_ok or not build_ok:
			raise PyvenException('Cleaning errors found')
		logger.info('STEP CLEAN : SUCCESSFUL')
	
# ============================================================================================================		

	@_step
	def retrieve(self, arg=None):
		self.configure()
		
		Pyven._log_step_delimiter()
		logger.info('STEP RETRIEVE : STARTING')
		for artifact in [a for a in self.objects['artifacts'].values() if a.to_retrieve]:
			if self.objects['repositories'][artifact.repo].is_available():
				self.objects['repositories'][artifact.repo].retrieve(artifact, Pyven.WORKSPACE)
				for package in self.objects['packages'].values():
					for item in [i for i in package.items if i.to_retrieve]:
						if artifact.format_name() == item.format_name():
							for built_artifact in [a for a in self.objects['artifacts'].values() if not a.to_retrieve]:
								dir = os.path.dirname(built_artifact.file)
								if not os.path.isdir(dir):
									os.makedirs(dir)
								shutil.copy(os.path.join(artifact.location(Pyven.WORKSPACE), artifact.basename()), os.path.join(dir, artifact.basename()))
			else:
				logger.error('Repository not accessible --> ' + self.objects['repositories'][artifact.repo].name + ' : ' + self.objects['repositories'][artifact.repo].url,\
							'Unable to retrieve artifact --> ' + artifact.format_name())
		logger.info('STEP RETRIEVE : SUCCESSFUL')

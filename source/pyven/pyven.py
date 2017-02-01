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

from pyven.utils.version_checking import VersionChecking

logger = logging.getLogger('global')

class Pyven:
	WORKSPACE = None
	if pyven.constants.PLATFORM == 'windows':
		LOCAL_REPO = Factory.create_repo('local', 'file', os.path.join(os.environ.get('USERPROFILE'), 'pvn_repo'))
	elif pyven.constants.PLATFORM == 'linux':
		LOCAL_REPO = Factory.create_repo('local', 'file', os.path.join(os.environ.get('HOME'), 'pvn_repo'))
	if not os.path.isdir(LOCAL_REPO.url):
		os.makedirs(LOCAL_REPO.url)

	def __init__(self, step, version, verbose=False, warning_as_error=False, pym='pym.xml'):
		logger.info('Initializing Pyven project')
		logger.info('Pyven set for '+pyven.constants.PLATFORM+' platform')
		logger.info('Local repository set at : ' + Pyven.LOCAL_REPO.url)
		
		self.step = step
		self.verbose = verbose
		if self.verbose:
			logger.info('Verbose mode enabled')
		self.warning_as_error = warning_as_error
		if self.warning_as_error:
			logger.info('Warnings will be considered as errors')
		self.pym = pym
		self.parser = PymParser(self.pym)
		self.objects = {'preprocessors': [], 'builders': [], 'unit_tests': [], 'integration_tests': []}
		self.version_checking = VersionChecking()
		
	def reportables(self):
		reportables = []
		if self.step in ['verify', 'install', 'deploy', 'deliver']:
			reportables.extend(self.objects['preprocessors'])
			reportables.extend(self.objects['builders'])
			reportables.append(self.version_checking)
			reportables.extend(self.objects['unit_tests'])
			reportables.extend(self.objects['valgrind_tests'])
			reportables.extend(self.objects['integration_tests'])
		elif self.step in ['test', 'package']:
			reportables.extend(self.objects['preprocessors'])
			reportables.extend(self.objects['builders'])
			reportables.append(self.version_checking)
			reportables.extend(self.objects['unit_tests'])
			reportables.extend(self.objects['valgrind_tests'])
		elif self.step in ['build']:
			reportables.extend(self.objects['preprocessors'])
			reportables.extend(self.objects['builders'])
			reportables.append(self.version_checking)
		return reportables
	
	@staticmethod
	def _log_step_delimiter():
		logger.info('===================================')
	
	@staticmethod
	def _set_workspace():
		Pyven.WORKSPACE = Factory.create_repo('workspace', 'workspace', 'pvn_workspace')
		if not os.path.isdir(Pyven.WORKSPACE.url):
			os.makedirs(Pyven.WORKSPACE.url)
		logger.info('Workspace set at : ' + Pyven.WORKSPACE.url)
	
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
			if repo.name == 'workspace' or repo.name == Pyven.LOCAL_REPO.name:
				logger.error('Repository name reserved --> ' + repo.name + ' : ' + repo.url)
			else:
				if repo.name in checked.keys():
					logger.error('Repository already added --> ' + repo.name + ' : ' + repo.url)
				else:
					checked[repo.name] = repo
					if repo.is_available():
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
				if not artifact.publish:
					logger.info('Artifact ' + artifact.format_name() + ' --> publishment disabled')
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
				if not package['package'].publish:
					logger.info('Package ' + package['package'].format_name() + ' --> publishment disabled')
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
	def _check_valgrind_tests(valgrind_tests):
		checked = []
		for valgrind_test in valgrind_tests:
			checked.append(valgrind_test)
			logger.info('Valgrind test added --> ' + os.path.join(valgrind_test.path, valgrind_test.filename))
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
	def _configure(self, arg=None):
		Pyven._log_step_delimiter()
		logger.info('STEP CONFIGURE : STARTING')
		self.objects = self.parser.parse()
		self.objects['repositories'] = self._check_repositories(self.objects['repositories'])
		self.objects['artifacts'] = self._check_artifacts(self.objects['artifacts'])
		self.objects['packages'] = self._check_packages(self.objects['packages'], self.objects['artifacts'])
		self.objects['preprocessors'] = self._check_preprocessors(self.objects['preprocessors'])
		self.objects['builders'] = self._check_builders(self.objects['builders'])
		self.objects['unit_tests'] = self._check_unit_tests(self.objects['unit_tests'])
		self.objects['valgrind_tests'] = self._check_valgrind_tests(self.objects['valgrind_tests'])
		self.objects['integration_tests'] = self._check_integration_tests(self.objects['integration_tests'], self.objects['packages'])
		logger.info('STEP CONFIGURE : SUCCESSFUL')
		
	def configure(self, arg=None):
		return self._configure(arg)
	
# ============================================================================================================		

	def __build(self, scope):
		if scope == 'preprocessors':
			sub_step = ('preprocessing', 'Preprocessing')
		elif scope == 'builders':
			sub_step = ('build', 'Build')
		
		logger.info('Starting ' + sub_step[0])
		ok = True
		for tool in self.objects[scope]:
			tic = time.time()
			if not tool.process(self.verbose, self.warning_as_error):
				ok = False
			else:
				toc = time.time()
				logger.info('Time for ' + tool.type + ':' + tool.name + ' : ' + str(round(toc - tic, 3)) + ' seconds')
		if not ok:
			raise PyvenException(sub_step[1] + ' errors found')
		logger.info(sub_step[1] + ' completed')
	
	@_step	
	def _build(self, arg=None):
		Pyven._log_step_delimiter()
		logger.info('STEP BUILD : STARTING')
		self.__build('preprocessors')
		self.__build('builders')
		ok = True
		for artifact in [a for a in self.objects['artifacts'].values() if not a.to_retrieve]:
			if not artifact.check(self.version_checking):
				ok = False
		if not ok:
			raise PyvenException('Artifacts missing')
		for artifact in [a for a in self.objects['artifacts'].values() if not a.to_retrieve]:
			Pyven.WORKSPACE.publish(artifact, artifact.file)
		logger.info('STEP BUILD : SUCCESSFUL')
		
	def build(self, arg=None):
		if self.configure():
			Pyven._set_workspace()
			return self._build(arg)
			
# ============================================================================================================		

	@staticmethod
	def __test(tests, verbose=False):
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
	def _test(self, arg=None):
		Pyven._log_step_delimiter()
		logger.info('STEP TEST : STARTING')
		if len(self.objects['unit_tests']) == 0:
			logger.warning('No unit tests found')
		else:
			if not Pyven.__test(self.objects['unit_tests'], self.verbose):
				raise PyvenException('Unit test failures found')
			if not Pyven.__test(self.objects['valgrind_tests'], self.verbose):
				raise PyvenException('Valgrind test failures found')
		logger.info('STEP TEST : SUCCESSFUL')

	def test(self, arg=None):
		if self.build():
			return self._test(arg)
			
# ============================================================================================================		

	@_step
	def _package(self, arg=None):
		Pyven._log_step_delimiter()
		logger.info('STEP PACKAGE : STARTING')
		ok = True
		for package in [p for p in self.objects['packages'].values() if not p.to_retrieve]:
			package_ok = True
			for artifact in [a for a in package.items if a.to_retrieve]:
				if self.objects['repositories'][artifact.repo].is_available():
					self.objects['repositories'][artifact.repo].retrieve(artifact, Pyven.WORKSPACE)
					logger.info('Repository ' + artifact.repo + ' --> Retrieved artifact ' + artifact.format_name())
				elif Pyven.LOCAL_REPO.is_available():
					logger.warning('Repository not accessible --> ' + self.objects['repositories'][artifact.repo].name + ' : ' + self.objects['repositories'][artifact.repo].url)
					Pyven.LOCAL_REPO.retrieve(artifact, Pyven.WORKSPACE)
					logger.warning('Local repository --> Retrieved artifact ' + artifact.format_name())
				else:
					logger.error('Local repository not accessible --> ' + Pyven.LOCAL_REPO.name + ' : ' + Pyven.LOCAL_REPO.url,\
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

	def package(self, arg=None):
		if self.test():
			return self._package(arg)
			
# ============================================================================================================		

	@_step
	def _verify(self, arg=None):
		Pyven._log_step_delimiter()
		logger.info('STEP VERIFY : STARTING')
		if len(self.objects['integration_tests']) == 0:
			logger.warning('No integration tests found')
		else:
			if not Pyven.__test(self.objects['integration_tests'], self.verbose):
				raise PyvenException('Integration test failures found')
		logger.info('STEP VERIFY : SUCCESSFUL')
		
	def verify(self, arg=None):
		if self.package():
			return self._verify(arg)
			
# ============================================================================================================		

	@_step
	def _install(self, arg=None):
		Pyven._log_step_delimiter()
		logger.info('STEP INSTALL : STARTING')
		for artifact in [a for a in self.objects['artifacts'].values() if a.publish]:
			self.LOCAL_REPO.publish(artifact, Pyven.WORKSPACE)
			logger.info('Repository ' + Pyven.LOCAL_REPO.name + ' --> Published artifact ' + artifact.format_name())
		for package in [p for p in self.objects['packages'].values() if p.publish]:
			self.LOCAL_REPO.publish(package, Pyven.WORKSPACE)
			logger.info('Repository ' + Pyven.LOCAL_REPO.name + ' --> Published package ' + package.format_name())
		logger.info('STEP INSTALL : SUCCESSFUL')
		
	def install(self, arg=None):
		if self.verify():
			return self._install(arg)
			
# ============================================================================================================		

	@_step
	def _deploy(self, repo=None):
		Pyven._log_step_delimiter()
		logger.info('STEP DEPLOY : STARTING')
		for repo in self.objects['repositories'].values():
			for artifact in [a for a in self.objects['artifacts'].values() if a.publish]:
				repo.publish(artifact, Pyven.WORKSPACE)
				logger.info('Repository ' + repo.name + ' --> Published artifact ' + artifact.format_name())
			for package in [p for p in self.objects['packages'].values() if p.publish]:
				repo.publish(package, Pyven.WORKSPACE)
				logger.info('Repository ' + repo.name + ' --> Published package ' + package.format_name())
		logger.info('STEP DEPLOY : SUCCESSFUL')
		
	def deploy(self, arg=None):
		if self.verify():
			return self._deploy(arg)
			
# ============================================================================================================		

	@_step
	def _deliver(self, path):
		Pyven._log_step_delimiter()
		logger.info('STEP DELIVER : STARTING')
		logger.info('Delivering to directory ' + path)
		for package in [p for p in self.objects['packages'].values() if p.publish]:
			if package.to_retrieve:
				if self.objects['repositories'][package.repo].is_available():
					package.deliver(path, self.objects['repositories'][package.repo])
				else:
					logger.error('Repository not accessible --> ' + self.objects['repositories'][artifact.repo].name + ' : ' + self.objects['repositories'][artifact.repo].url,\
							'Unable to retrieve package --> ' + package.format_name())
			else:
				Pyven._set_workspace()
				package.deliver(path, Pyven.WORKSPACE)
			logger.info('Delivered package : ' + package.format_name())
		logger.info('STEP DELIVER : SUCCESSFUL')
		
	def deliver(self, arg=None):
		if self.configure():
			return self._deliver(arg)
			
# ============================================================================================================		

	@_step
	def _clean(self, arg=None):
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
	
	def clean(self, arg=None):
		if self.configure():
			return self._clean(arg)
			
# ============================================================================================================		

	@_step
	def _retrieve(self, arg=None):
		Pyven._log_step_delimiter()
		logger.info('STEP RETRIEVE : STARTING')
		for package in [p for p in self.objects['packages'].values() if p.to_retrieve]:
			if self.objects['repositories'][package.repo].is_available():
				self.objects['repositories'][package.repo].retrieve(package, Pyven.WORKSPACE)
			else:
				logger.error('Repository not accessible --> ' + self.objects['repositories'][artifact.repo].name + ' : ' + self.objects['repositories'][artifact.repo].url,\
							'Unable to retrieve package --> ' + package.format_name())
		for artifact in [a for a in self.objects['artifacts'].values() if a.to_retrieve]:
			if self.objects['repositories'][artifact.repo].is_available():
				self.objects['repositories'][artifact.repo].retrieve(artifact, Pyven.WORKSPACE)
			else:
				logger.error('Repository not accessible --> ' + self.objects['repositories'][artifact.repo].name + ' : ' + self.objects['repositories'][artifact.repo].url,\
							'Unable to retrieve artifact --> ' + artifact.format_name())
		for package in [p for p in self.objects['packages'].values() if not p.to_retrieve]:
			for item in [i for i in package.items if i.to_retrieve]:
				for built_item in [i for i in package.items if not i.to_retrieve]:
					dir = os.path.dirname(built_item.file)
					if not os.path.isdir(dir):
						os.makedirs(dir)
					logger.info('Copying artifact ' + item.format_name() + ' to directory ' + dir)
					shutil.copy(os.path.join(item.location(Pyven.WORKSPACE.url), item.basename()), os.path.join(dir, item.basename()))
		logger.info('STEP RETRIEVE : SUCCESSFUL')

	def retrieve(self, arg=None):
		if self.configure():
			Pyven._set_workspace()
			return self._retrieve(arg)
			
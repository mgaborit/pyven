import logging, os, shutil, time
from lxml import etree

import pyven.constants
from pyven.exceptions.exception import PyvenException
from pyven.exceptions.repository_exception import RepositoryException

from pyven.items.artifact import Artifact
from pyven.items.package import Package

from pyven.repositories.directory import DirectoryRepo
from pyven.repositories.workspace import Workspace

from pyven.processing.tools.tool import Tool
from pyven.processing.tests.test import Test

from pyven.parser.pym_parser import PymParser

from pyven.checkers.checker import Checker

logger = logging.getLogger('global')

class Pyven:
	WORKSPACE = None
	if pyven.constants.PLATFORM == 'windows':
		LOCAL_REPO = DirectoryRepo('local', 'file', os.path.join(os.environ.get('USERPROFILE'), 'pvn_repo'))
	elif pyven.constants.PLATFORM == 'linux':
		LOCAL_REPO = DirectoryRepo('local', 'file', os.path.join(os.environ.get('HOME'), 'pvn_repo'))
	if not os.path.isdir(LOCAL_REPO.url):
		os.makedirs(LOCAL_REPO.url)

	def __init__(self, step, verbose=False, warning_as_error=False, pym='pym.xml', path=''):
		
		self.pym = pym
		self.path = path
		logger.info(self._project_log() + 'Initializing Pyven project')
		self.step = step
		self.verbose = verbose
		if self.verbose:
			logger.info(self._project_log() + 'Verbose mode enabled')
		self.warning_as_error = warning_as_error
		if self.warning_as_error:
			logger.info(self._project_log() + 'Warnings will be considered as errors')
		self.parser = PymParser(os.path.join(self.path, self.pym))
		self.objects = {'subprojects' : []}
		self.checkers = {'artifacts' : Checker('Artifacts'),\
						'package' : Checker('Packaging'),\
						'retrieve' : Checker('Retrieval')}
		
	def reportables(self):
		reportables = []
		if self.step in ['verify', 'install', 'deploy', 'deliver']:
			if self.parser.checker.enabled():
				reportables.append(self.parser.checker)
			else:
				reportables.extend(self.objects['preprocessors'])
				reportables.extend(self.objects['builders'])
				if self.checkers['artifacts'].enabled():
					reportables.append(self.checkers['artifacts'])
				if self.checkers['package'].enabled():
					reportables.append(self.checkers['package'])
				reportables.extend(self.objects['unit_tests'])
				reportables.extend(self.objects['valgrind_tests'])
				reportables.extend(self.objects['integration_tests'])
		elif self.step in ['test', 'package']:
			if self.parser.checker.enabled():
				reportables.append(self.parser.checker)
			else:
				reportables.extend(self.objects['preprocessors'])
				reportables.extend(self.objects['builders'])
				if self.checkers['artifacts'].enabled():
					reportables.append(self.checkers['artifacts'])
				if self.checkers['package'].enabled():
					reportables.append(self.checkers['package'])
				reportables.extend(self.objects['unit_tests'])
				reportables.extend(self.objects['valgrind_tests'])
		elif self.step in ['build']:
			if self.parser.checker.enabled():
				reportables.append(self.parser.checker)
			else:
				reportables.extend(self.objects['preprocessors'])
				reportables.extend(self.objects['builders'])
				if self.checkers['artifacts'].enabled():
					reportables.append(self.checkers['artifacts'])
		else:
			reportables.append(self.parser.checker)
		return reportables
	
	@staticmethod
	def _step_log_delimiter():
		logger.info('===================================')
	
	@staticmethod
	def _set_workspace():
		if Pyven.WORKSPACE is None:
			Pyven.WORKSPACE = Workspace('workspace', 'workspace', os.path.join(os.getcwd(), 'pvn_workspace'))
			if not os.path.isdir(Pyven.WORKSPACE.url):
				os.makedirs(Pyven.WORKSPACE.url)
			logger.info('Workspace set at : ' + Pyven.WORKSPACE.url)
	
	def _step(function, arg=None):
		def __intern(self=None, arg=None):
			Pyven._step_log_delimiter()
			logger.info(self._project_log() + 'STEP ' + function.__name__.replace('_', '').upper() + ' : STARTING')
			Pyven._step_log_delimiter()
			ok = True
			try:
				tic = time.time()
				ok = function(self, arg)
				toc = time.time()
				logger.info(self._project_log() + 'Step time : ' + str(round(toc - tic, 3)) + ' seconds')
			except PyvenException as e:
				for msg in e.args:
					logger.error(self._project_log() + msg)
				ok = False
			if ok:
				Pyven._step_log_delimiter()
				logger.info(self._project_log() + 'STEP ' + function.__name__.replace('_', '').upper() + ' : SUCCESSFUL')
				Pyven._step_log_delimiter()
			else:
				Pyven._step_log_delimiter()
				logger.error(self._project_log() + 'STEP ' + function.__name__.replace('_', '').upper() + ' : FAILED')
				Pyven._step_log_delimiter()
			return ok
		return __intern
		
	def _project_log(self):
		log = ''
		if self.path != '':
			log = '[' + self.path + '] '
		return log
		
# ============================================================================================================		

	def _check(function):
		def __intern(self=None):
			ok = True
			try:
				function(self)
			except PyvenException as e:
				for msg in e.args:
					logger.error(self._project_log() + msg)
				ok = False
			return ok
		return __intern
		
	@_check
	def _check_subprojects(self):
		checked = []
		for subdirectory in self.objects['subprojects']:
			if not os.path.isdir(subdirectory) or 'pym.xml' not in os.listdir(subdirectory):
				raise PyvenException(self._project_log() + 'No pym.xml file found at ' + subdirectory)
			else:
				subproject = Pyven(step=self.step, verbose=self.verbose, warning_as_error=self.warning_as_error, pym=self.pym, path=os.path.join(self.path, subdirectory))
				checked.append(subproject)
				logger.info(self._project_log() + 'Added subproject --> ' + subdirectory)
		self.objects['subprojects'] = checked
	
	@_check
	def _check_repositories(self):
		checked = {}
		for repo in self.objects['repositories']:
			if repo.name == 'workspace' or repo.name == Pyven.LOCAL_REPO.name:
				raise PyvenException(self._project_log() + 'Repository name reserved --> ' + repo.name + ' : ' + repo.url)
			else:
				if repo.name in checked.keys():
					raise PyvenException(self._project_log() + 'Repository already added --> ' + repo.name + ' : ' + repo.url)
				else:
					checked[repo.name] = repo
					if repo.is_available():
						logger.info(self._project_log() + 'Repository added --> ' + repo.name + ' : ' + repo.url)
					else:
						logger.warning(self._project_log() + 'Repository not accessible --> ' + repo.name + ' : ' + repo.url)
		self.objects['repositories'] = checked
		
	@_check
	def _check_artifacts(self):
		checked = {}
		for artifact in self.objects['artifacts']:
			if artifact.format_name() in checked.keys():
				raise PyvenException(self._project_log() + 'Artifact already added --> ' + artifact.format_name())
			else:
				checked[artifact.format_name()] = artifact
				logger.info(self._project_log() + 'Artifact added --> ' + artifact.format_name())
				if not artifact.publish:
					logger.info(self._project_log() + 'Artifact ' + artifact.format_name() + ' --> publishment disabled')
		self.objects['artifacts'] = checked
		
	@_check
	def _check_packages(self):
		checked = {}
		for package in self.objects['packages']:
			items = []
			items.extend(package.items)
			package.items = []
			if package.format_name() in checked.keys():
				raise PyvenException(self._project_log() + 'Package already added --> ' + package.format_name())
			else:
				for item in items:
					if item not in self.objects['artifacts'].keys():
						raise PyvenException(self._project_log() + 'Package ' + package.format_name() + ' : Artifact not declared --> ' + item)
					else:
						package.items.append(self.objects['artifacts'][item])
						logger.info(self._project_log() + 'Package ' + package.format_name() + ' : Artifact added --> ' + item)
				checked[package.format_name()] = package
				logger.info(self._project_log() + 'Package added --> ' + package.format_name())
				if not package.publish:
					logger.info(self._project_log() + 'Package ' + package.format_name() + ' --> publishment disabled')
		self.objects['packages'] = checked
		
	@_check
	def _check_preprocessors(self):
		checked = []
		for preprocessor in self.objects['preprocessors']:
			checked.append(preprocessor)
			logger.info(self._project_log() + 'Preprocessor added --> ' + preprocessor.type + ':' + preprocessor.name)
		self.objects['preprocessors'] = checked
		
	@_check
	def _check_builders(self):
		checked = []
		for builder in self.objects['builders']:
			checked.append(builder)
			logger.info(self._project_log() + 'Builder added --> ' + builder.type + ':' + builder.name)
		self.objects['builders'] = checked
		
	@_check
	def _check_unit_tests(self):
		checked = []
		for unit_test in self.objects['unit_tests']:
			checked.append(unit_test)
			logger.info(self._project_log() + 'Unit test added --> ' + os.path.join(unit_test.path, unit_test.filename))
		self.objects['unit_tests'] = checked
		
	@_check
	def _check_valgrind_tests(self):
		checked = []
		for valgrind_test in self.objects['valgrind_tests']:
			checked.append(valgrind_test)
			logger.info(self._project_log() + 'Valgrind test added --> ' + os.path.join(valgrind_test.path, valgrind_test.filename))
		self.objects['valgrind_tests'] = checked
		
	@_check
	def _check_integration_tests(self):
		checked = []
		for integration_test in self.objects['integration_tests']:
			if integration_test.package not in self.objects['packages'].keys():
				raise PyvenException(self._project_log() + 'Integration test ' + os.path.join(integration_test.path, integration_test.filename)\
							+ ' : Package not declared --> ' + integration_test.package)
			else:
				integration_test.package = self.objects['packages'][integration_test.package]
				logger.info(self._project_log() + 'Integration test ' + os.path.join(integration_test.path, integration_test.filename)\
							+ ' : Package added --> ' + integration_test.package.format_name())
			checked.append(integration_test)
			logger.info(self._project_log() + 'Integration test added --> ' + os.path.join(integration_test.path, integration_test.filename))
		self.objects['integration_tests'] = checked
		
	@_step
	def _configure(self, arg=None):
		ok = True
		if self.step != 'deliver':
			Pyven._set_workspace()
		self.objects = self.parser.parse()
		if not self._check_subprojects():
			ok = False
		else:
			for subproject in self.objects['subprojects']:
				if not subproject.configure():
					ok = False
		if not ok or not self._check_repositories():
			ok = False
		elif not self._check_artifacts():
			ok = False
		elif not self._check_packages():
			ok = False
		elif not self._check_preprocessors():
			ok = False
		elif not self._check_builders():
			ok = False
		elif not self._check_unit_tests():
			ok = False
		elif not self._check_valgrind_tests():
			ok = False
		elif not self._check_integration_tests():
			ok = False
		return ok
		
	def configure(self, arg=None):
		return self._configure(arg)
	
# ============================================================================================================		

	def __build(self, scope):
		if scope == 'preprocessors':
			sub_step = ('preprocessing', 'Preprocessing')
		elif scope == 'builders':
			sub_step = ('build', 'Build')
		
		logger.info(self._project_log() + 'Starting ' + sub_step[0])
		ok = True
		for tool in self.objects[scope]:
			tic = time.time()
			if not tool.process(self.verbose, self.warning_as_error):
				ok = False
			else:
				toc = time.time()
				logger.info(self._project_log() + 'Time for ' + tool.type + ':' + tool.name + ' : ' + str(round(toc - tic, 3)) + ' seconds')
		if not ok:
			raise PyvenException(sub_step[1] + ' errors found')
		logger.info(self._project_log() + sub_step[1] + ' completed')
	
	@_step	
	def _build(self, arg=None):
		ok = True
		for subproject in self.objects['subprojects']:
			os.chdir(subproject.path)
			if not subproject._build():
				ok = False
			for dir in subproject.path.split(os.sep):
				os.chdir('..')
		self.__build('preprocessors')
		self.__build('builders')
		for artifact in [a for a in self.objects['artifacts'].values() if not a.to_retrieve]:
			if not artifact.check(self.checkers['artifacts']):
				ok = False
		if not ok:
			raise PyvenException('Artifacts missing')
		for artifact in [a for a in self.objects['artifacts'].values() if not a.to_retrieve]:
			Pyven.WORKSPACE.publish(artifact, artifact.file)
		return ok
		
	def build(self, arg=None):
		if self.configure():
			return self._build(arg)
			
# ============================================================================================================		

	def __test(self, tests, verbose=False):
		ok = True
		for test in tests:
			tic = time.time()
			if not test.process(verbose, Pyven.WORKSPACE):
				ok = False
			else:
				toc = time.time()
				logger.info(self._project_log() + 'Time for test ' + test.filename + ' : ' + str(round(toc - tic, 3)) + ' seconds')
		return ok

	@_step
	def _test(self, arg=None):
		ok = True
		for subproject in self.objects['subprojects']:
			os.chdir(subproject.path)
			if not subproject._test():
				ok = False
			for dir in subproject.path.split(os.sep):
				os.chdir('..')
		if len(self.objects['unit_tests']) == 0:
			logger.warning(self._project_log() + 'No unit tests found')
		else:
			if not self.__test(self.objects['unit_tests'], self.verbose):
				raise PyvenException('Unit test failures found')
			if not self.__test(self.objects['valgrind_tests'], self.verbose):
				raise PyvenException('Valgrind test failures found')
		return ok

	def test(self, arg=None):
		if self.build():
			return self._test(arg)
			
# ============================================================================================================		

	@_step
	def _package(self, arg=None):
		ok = True
		for subproject in self.objects['subprojects']:
			if not subproject._package():
				ok = False
		for package in [p for p in self.objects['packages'].values() if not p.to_retrieve]:
			package_ok = True
			for artifact in [a for a in package.items if a.to_retrieve]:
				try:
					if self.objects['repositories'][artifact.repo].is_available():
						self.objects['repositories'][artifact.repo].retrieve(artifact, Pyven.WORKSPACE)
						logger.info(self._project_log() + 'Repository ' + artifact.repo + ' --> Retrieved artifact ' + artifact.format_name())
					elif Pyven.LOCAL_REPO.is_available():
						logger.warning(self._project_log() + 'Repository not accessible --> ' + self.objects['repositories'][artifact.repo].name + ' : ' + self.objects['repositories'][artifact.repo].url)
						Pyven.LOCAL_REPO.retrieve(artifact, Pyven.WORKSPACE)
						logger.warning(self._project_log() + 'Local repository --> Retrieved artifact ' + artifact.format_name())
					else:
						raise RepositoryException('Unable to retrieve artifact --> ' + artifact.format_name(),\
													'Unable to build package --> ' + package.format_name())
				except RepositoryException as e:
					for msg in e.args:
						logger.error(self._project_log() + msg)
					package_ok = False
					ok = False
			if package_ok:
				if not package.pack(Pyven.WORKSPACE):
					ok = False
		if not ok:
			raise PyvenException('Some packages were not built')
		return ok

	def package(self, arg=None):
		if self.test():
			return self._package(arg)
			
# ============================================================================================================		

	@_step
	def _verify(self, arg=None):
		ok = True
		for subproject in self.objects['subprojects']:
			os.chdir(subproject.path)
			if not subproject._verify():
				ok = False
			for dir in subproject.path.split(os.sep):
				os.chdir('..')
		if len(self.objects['integration_tests']) == 0:
			logger.warning(self._project_log() + 'No integration tests found')
		else:
			if not self.__test(self.objects['integration_tests'], self.verbose):
				raise PyvenException('Integration test failures found')
		return ok
		
	def verify(self, arg=None):
		if self.package():
			return self._verify(arg)
			
# ============================================================================================================		

	@_step
	def _install(self, arg=None):
		ok = True
		for subproject in self.objects['subprojects']:
			if not subproject._install():
				ok = False
		for artifact in [a for a in self.objects['artifacts'].values() if a.publish]:
			Pyven.LOCAL_REPO.publish(artifact, Pyven.WORKSPACE)
			logger.info(self._project_log() + 'Repository ' + Pyven.LOCAL_REPO.name + ' --> Published artifact ' + artifact.format_name())
		for package in [p for p in self.objects['packages'].values() if p.publish]:
			Pyven.LOCAL_REPO.publish(package, Pyven.WORKSPACE)
			logger.info(self._project_log() + 'Repository ' + Pyven.LOCAL_REPO.name + ' --> Published package ' + package.format_name())
		return ok
		
	def install(self, arg=None):
		if self.verify():
			return self._install(arg)
			
# ============================================================================================================		

	@_step
	def _deploy(self, repo=None):
		ok = True
		for subproject in self.objects['subprojects']:
			if not subproject._deploy():
				ok = False
		for repo in self.objects['repositories'].values():
			for artifact in [a for a in self.objects['artifacts'].values() if a.publish]:
				repo.publish(artifact, Pyven.WORKSPACE)
				logger.info(self._project_log() + 'Repository ' + repo.name + ' --> Published artifact ' + artifact.format_name())
			for package in [p for p in self.objects['packages'].values() if p.publish]:
				repo.publish(package, Pyven.WORKSPACE)
				logger.info(self._project_log() + 'Repository ' + repo.name + ' --> Published package ' + package.format_name())
		return ok
		
	def deploy(self, arg=None):
		if self.verify():
			return self._deploy(arg)
			
# ============================================================================================================		

	@_step
	def _deliver(self, path):
		ok = True
		for subproject in self.objects['subprojects']:
			os.chdir(subproject.path)
			if not subproject._deliver():
				ok = False
			for dir in subproject.path.split(os.sep):
				os.chdir('..')
		logger.info(self._project_log() + 'Delivering to directory ' + path)
		for package in [p for p in self.objects['packages'].values() if p.publish]:
			if package.to_retrieve:
				if self.objects['repositories'][package.repo].is_available():
					package.deliver(path, self.objects['repositories'][package.repo])
				else:
					logger.error(self._project_log() + 'Repository not accessible --> ' + self.objects['repositories'][artifact.repo].name + ' : ' + self.objects['repositories'][artifact.repo].url,\
							'Unable to retrieve package --> ' + package.format_name())
			else:
				Pyven._set_workspace()
				package.deliver(path, Pyven.WORKSPACE)
			logger.info(self._project_log() + 'Delivered package : ' + package.format_name())
		return ok
		
	def deliver(self, arg=None):
		if self.configure():
			return self._deliver(arg)
			
# ============================================================================================================		

	@_step
	def _clean(self, arg=None):
		ok = True
		for subproject in self.objects['subprojects']:
			os.chdir(subproject.path)
			if not subproject._clean():
				ok = False
			for dir in subproject.path.split(os.sep):
				os.chdir('..')
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
		return ok and build_ok and preprocess_ok
	
	def clean(self, arg=None):
		if self.configure():
			return self._clean(arg)
			
# ============================================================================================================		

	@_step
	def _retrieve(self, arg=None):
		ok = True
		for subproject in self.objects['subprojects']:
			os.chdir(subproject.path)
			if not subproject._retrieve():
				ok = False
			for dir in subproject.path.split(os.sep):
				os.chdir('..')
		for package in [p for p in self.objects['packages'].values() if p.to_retrieve]:
			try:
				if self.objects['repositories'][package.repo].is_available():
					self.objects['repositories'][package.repo].retrieve(package, Pyven.WORKSPACE)
				else:
					raise RepositoryException(self._project_log() + 'Repository not accessible --> ' + self.objects['repositories'][artifact.repo].name + ' : ' + self.objects['repositories'][artifact.repo].url,\
												'Unable to retrieve package --> ' + package.format_name())
			except RepositoryException as e:
				for msg in e.args:
					logger.error(msg)
				ok = False
		for artifact in [a for a in self.objects['artifacts'].values() if a.to_retrieve]:
			try:
				if self.objects['repositories'][artifact.repo].is_available():
					self.objects['repositories'][artifact.repo].retrieve(artifact, Pyven.WORKSPACE)
				else:
					raise RepositoryException(self._project_log() + 'Repository not accessible --> ' + self.objects['repositories'][artifact.repo].name + ' : ' + self.objects['repositories'][artifact.repo].url,\
												'Unable to retrieve artifact --> ' + artifact.format_name())
			except RepositoryException as e:
				for msg in e.args:
					logger.error(msg)
				ok = False
		if ok:
			for package in [p for p in self.objects['packages'].values() if not p.to_retrieve]:
				for item in [i for i in package.items if i.to_retrieve]:
					for built_item in [i for i in package.items if not i.to_retrieve]:
						dir = os.path.dirname(built_item.file)
						if not os.path.isdir(dir):
							os.makedirs(dir)
						logger.info(self._project_log() + 'Copying artifact ' + item.format_name() + ' to directory ' + dir)
						shutil.copy(os.path.join(item.location(Pyven.WORKSPACE.url), item.basename()), os.path.join(dir, item.basename()))
		return ok

	def retrieve(self, arg=None):
		if self.configure():
			return self._retrieve(arg)
			
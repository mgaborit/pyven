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

from pyven.reporting.reportable import Reportable
from pyven.processing.processible import Processible

from pyven.steps.step import Step
from pyven.steps.preprocess import Preprocess
from pyven.steps.build import Build
from pyven.steps.artifacts_checks import ArtifactsChecks
from pyven.steps.unit_tests import UnitTests
from pyven.steps.package import PackageStep
from pyven.steps.integration_tests import IntegrationTests
from pyven.steps.deploy import Deploy
from pyven.steps.retrieve import Retrieve
from pyven.steps.deliver import Deliver

logger = logging.getLogger('global')

class Pyven:
	WORKSPACE = Workspace('workspace', 'workspace', os.path.join(os.getcwd(), 'pvn_workspace'))
	if pyven.constants.PLATFORM == 'windows':
		LOCAL_REPO = DirectoryRepo('local', 'file', os.path.join(os.environ.get('USERPROFILE'), 'pvn_repo'))
	elif pyven.constants.PLATFORM == 'linux':
		LOCAL_REPO = DirectoryRepo('local', 'file', os.path.join(os.environ.get('HOME'), 'pvn_repo'))
	if not os.path.isdir(LOCAL_REPO.url):
		os.makedirs(LOCAL_REPO.url)

	def __init__(self, step, verbose=False, warning_as_error=False, pym='pym.xml', release=False, path=''):
		
		self.pym = pym
		self.path = path
		logger.info(self._project_log() + 'Initializing Pyven project')
		self.step = step
		self.verbose = verbose
		if self.verbose:
			logger.info(self._project_log() + 'Verbose mode enabled')
		self.release = release
		if self.release:
			logger.info(self._project_log() + 'Release mode enabled')
		self.warning_as_error = warning_as_error
		if self.warning_as_error:
			logger.info(self._project_log() + 'Warnings will be considered as errors')
		self.parser = PymParser(os.path.join(self.path, self.pym))
		self.constants = {}
		self.objects = {'subprojects' : [],\
						'repositories' : {},\
						'artifacts' : {},\
						'packages' : {},\
						'preprocessors' : [],\
						'builders' : [],\
						'unit_tests' : [],\
						'valgrind_tests' : [],\
						'integration_tests' : []}
		self.checkers = {'artifacts' : Checker('Artifacts'),\
						'package' : Checker('Packaging'),\
						'retrieve' : Checker('Retrieval'),\
						'configuration' : Checker('Configuration'),\
						'deployment' : Checker('Deployment')}
		self.preprocess = Preprocess(self.path, self.verbose)
		self.build2 = Build(self.path, self.verbose, self.warning_as_error)
		self.artifacts_checks = ArtifactsChecks(self.path, self.verbose)
		self.unit_tests = UnitTests(self.path, self.verbose)
		self.package2 = PackageStep(self.path, self.verbose)
		self.integration_tests = IntegrationTests(self.path, self.verbose)
		self.deploy2 = Deploy(self.path, self.verbose, self.release)
		self.retrieve2 = Retrieve(self.path, self.verbose)
		self.deliver2 = Deliver(self.path, self.verbose, '')
		
	def reportables(self):
		reportables = []
		if self.step in ['verify', 'install', 'deploy']:
			if self.parser.checker.enabled():
				reportables.append(self.parser.checker)
			elif self.checkers['configuration'].enabled():
				reportables.append(self.checkers['configuration'])
			else:
				reportables.extend(self.preprocess.tools)
				if self.preprocess.checker.enabled():
					reportables.append(self.preprocess.checker)
				reportables.extend(self.build2.tools)
				if self.build2.checker.enabled():
					reportables.append(self.build2.checker)
				if self.artifacts_checks.checker.enabled():
					reportables.append(self.artifacts_checks.checker)
				reportables.extend(self.unit_tests.tests)
				if self.unit_tests.checker.enabled():
					reportables.append(self.unit_tests.checker)
				if self.package2.checker.enabled():
					reportables.append(self.package2.checker)
				reportables.extend(self.objects['valgrind_tests'])
				reportables.extend(self.integration_tests.tests)
				if self.integration_tests.checker.enabled():
					reportables.append(self.integration_tests.checker)
				if self.deploy2.checker.enabled():
					reportables.append(self.deploy2.checker)
		elif self.step in ['test', 'package']:
			if self.parser.checker.enabled():
				reportables.append(self.parser.checker)
			elif self.checkers['configuration'].enabled():
				reportables.append(self.checkers['configuration'])
			else:
				reportables.extend(self.preprocess.tools)
				if self.preprocess.checker.enabled():
					reportables.append(self.preprocess.checker)
				reportables.extend(self.build2.tools)
				if self.build2.checker.enabled():
					reportables.append(self.build2.checker)
				if self.artifacts_checks.checker.enabled():
					reportables.append(self.artifacts_checks.checker)
				reportables.extend(self.unit_tests.tests)
				if self.unit_tests.checker.enabled():
					reportables.append(self.unit_tests.checker)
				if self.package2.checker.enabled():
					reportables.append(self.package2.checker)
				reportables.extend(self.objects['valgrind_tests'])
		elif self.step in ['build']:
			if self.parser.checker.enabled():
				reportables.append(self.parser.checker)
			elif self.checkers['configuration'].enabled():
				reportables.append(self.checkers['configuration'])
			else:
				reportables.extend(self.preprocess.tools)
				if self.preprocess.checker.enabled():
					reportables.append(self.preprocess.checker)
				reportables.extend(self.build2.tools)
				if self.build2.checker.enabled():
					reportables.append(self.build2.checker)
				if self.artifacts_checks.checker.enabled():
					reportables.append(self.artifacts_checks.checker)
		elif self.step in ['retrieve']:
			if self.parser.checker.enabled():
				reportables.append(self.parser.checker)
			elif self.checkers['configuration'].enabled():
				reportables.append(self.checkers['configuration'])
			else:
				reportables.append(self.retrieve2.checker)
		elif self.step in ['deliver']:
			if self.parser.checker.enabled():
				reportables.append(self.parser.checker)
			elif self.checkers['configuration'].enabled():
				reportables.append(self.checkers['configuration'])
			else:
				reportables.append(self.deliver2.checker)
		elif self.step in ['parse']:
			reportables.extend(self.objects['unit_tests'])
		else:
			reportables.append(self.parser.checker)
			reportables.append(self.checkers['configuration'])
		return reportables
	
	@staticmethod
	def _step_log_delimiter():
		logger.info('===================================')
	
	def _set_workspace(self):
		if not os.path.isdir(Pyven.WORKSPACE.url):
			os.makedirs(Pyven.WORKSPACE.url)
		logger.info('Workspace set at : ' + Pyven.WORKSPACE.url)
		self.objects['repositories'][Pyven.WORKSPACE.name] = Pyven.WORKSPACE
		Step.WORKSPACE = Pyven.WORKSPACE
	
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

	def _replace_constants(self, str):
		for name, value in self.constants.items():
			str = str.replace('$('+name+')', value)
		return str

	def _check(function, objects=None):
		def __intern(self=None, objects=None):
			ok = True
			try:
				function(self, objects)
			except PyvenException as e:
				self.checkers['configuration'].errors.append(e.args)
				for msg in e.args:
					logger.error(self._project_log() + msg)
				ok = False
			return ok
		return __intern
		
	@_check
	def _check_subprojects(self, objects):
		for subdirectory in objects['subprojects']:
			if not os.path.isdir(subdirectory):
				raise PyvenException('Subproject directory does not exist : ' + subdirectory)
			elif self.pym not in os.listdir(subdirectory):
				raise PyvenException('No ' + self.pym + ' file found at ' + subdirectory)
			else:
				subproject = Pyven(step=self.step, verbose=self.verbose, warning_as_error=self.warning_as_error, pym=self.pym, path=os.path.join(self.path, subdirectory))
				self.objects['subprojects'].append(subproject)
				logger.info(self._project_log() + 'Added subproject --> ' + subdirectory)
	
	@_check
	def _check_repositories(self, objects):
		for repo in objects['repositories']:
			if repo.name == 'workspace' or repo.name == Pyven.LOCAL_REPO.name:
				raise PyvenException('Repository name reserved --> ' + repo.name + ' : ' + repo.url)
			else:
				if repo.name in self.objects['repositories'].keys():
					raise PyvenException('Repository already added --> ' + repo.name + ' : ' + repo.url)
				else:
					self.objects['repositories'][repo.name] = repo
					if repo.is_reachable():
						if repo.release:
							logger.info(self._project_log() + 'Release repository added --> ' + repo.name + ' : ' + repo.url)
						else:
							logger.info(self._project_log() + 'Repository added --> ' + repo.name + ' : ' + repo.url)
					else:
						logger.warning('Repository not accessible --> ' + repo.name + ' : ' + repo.url)
		self.package2.repositories = self.objects['repositories']
		self.deploy2.repositories = self.objects['repositories']
		self.retrieve2.repositories = self.objects['repositories']
		self.deliver2.repositories = self.objects['repositories']
		
	@_check
	def _check_artifacts(self, objects):
		for artifact in objects['artifacts']:
			artifact.company = self._replace_constants(artifact.company)
			artifact.name = self._replace_constants(artifact.name)
			artifact.config = self._replace_constants(artifact.config)
			artifact.version = self._replace_constants(artifact.version)
			if not artifact.to_retrieve:
				artifact.file = self._replace_constants(artifact.file)
			if artifact.format_name() in self.objects['artifacts'].keys():
				raise PyvenException('Artifact already added --> ' + artifact.format_name())
			elif artifact.to_retrieve and artifact.repo not in self.objects['repositories'].keys() and artifact.repo not in [Pyven.LOCAL_REPO.name, 'workspace']:
				raise PyvenException('Artifact repository not declared --> ' + artifact.format_name() + ' : repo ' + artifact.repo)
			else:
				self.objects['artifacts'][artifact.format_name()] = artifact
				logger.info(self._project_log() + 'Artifact added --> ' + artifact.format_name())
				if not artifact.publish:
					logger.info(self._project_log() + 'Artifact ' + artifact.format_name() + ' --> publishment disabled')
		self.artifacts_checks.artifacts = self.objects['artifacts']
		self.package2.artifacts = self.objects['artifacts']
		self.deploy2.artifacts = self.objects['artifacts']
		self.retrieve2.artifacts = self.objects['artifacts']
		
	@_check
	def _check_packages(self, objects):
		for package in objects['packages']:
			package.company = self._replace_constants(package.company)
			package.name = self._replace_constants(package.name)
			package.config = self._replace_constants(package.config)
			package.version = self._replace_constants(package.version)
			package.delivery = self._replace_constants(package.delivery)
			items = []
			items.extend(package.items)
			package.items = []
			if package.format_name() in self.objects['packages'].keys():
				raise PyvenException('Package already added --> ' + package.format_name())
			elif package.to_retrieve and package.repo not in self.objects['repositories'].keys() and package.repo not in [Pyven.LOCAL_REPO.name, 'workspace']:
				raise PyvenException('Package repository not declared --> ' + package.format_name() + ' : repo ' + package.repo)
			else:
				for item in items:
					item = self._replace_constants(item)
					if item not in self.objects['artifacts'].keys():
						raise PyvenException('Package ' + package.format_name() + ' : Artifact not declared --> ' + item)
					else:
						package.items.append(self.objects['artifacts'][item])
						logger.info(self._project_log() + 'Package ' + package.format_name() + ' : Artifact added --> ' + item)
				self.objects['packages'][package.format_name()] = package
				logger.info(self._project_log() + 'Package added --> ' + package.format_name())
				if not package.publish:
					logger.info(self._project_log() + 'Package ' + package.format_name() + ' --> publishment disabled')
		self.package2.packages = self.objects['packages']
		self.deploy2.packages = self.objects['packages']
		self.retrieve2.packages = self.objects['packages']
		self.deliver2.packages = self.objects['packages']
		
	@_check
	def _check_preprocessors(self, objects):
		checked = []
		for preprocessor in objects['preprocessors']:
			preprocessor.name = self._replace_constants(preprocessor.name)
			checked.append(preprocessor)
			logger.info(self._project_log() + 'Preprocessor added --> ' + preprocessor.type + ':' + preprocessor.name)
		self.preprocess.tools = checked
		
	@_check
	def _check_builders(self, objects):
		checked = []
		for builder in objects['builders']:
			builder.name = self._replace_constants(builder.name)
			checked.append(builder)
			logger.info(self._project_log() + 'Builder added --> ' + builder.type + ':' + builder.name)
		self.build2.tools = checked
		
	@_check
	def _check_unit_tests(self, objects):
		checked = []
		for unit_test in objects['unit_tests']:
			checked.append(unit_test)
			logger.info(self._project_log() + 'Unit test added --> ' + os.path.join(unit_test.path, unit_test.filename))
		self.unit_tests.tests = checked
		
	@_check
	def _check_valgrind_tests(self, objects):
		checked = []
		for valgrind_test in objects['valgrind_tests']:
			checked.append(valgrind_test)
			logger.info(self._project_log() + 'Valgrind test added --> ' + os.path.join(valgrind_test.path, valgrind_test.filename))
		self.objects['valgrind_tests'] = checked
		
	@_check
	def _check_integration_tests(self, objects):
		checked = []
		for integration_test in objects['integration_tests']:
			integration_test.package = self._replace_constants(integration_test.package)
			if integration_test.package not in self.objects['packages'].keys():
				raise PyvenException('Integration test ' + os.path.join(integration_test.path, integration_test.filename)\
							+ ' : Package not declared --> ' + integration_test.package)
			else:
				integration_test.package = self.objects['packages'][integration_test.package]
				logger.info(self._project_log() + 'Integration test ' + os.path.join(integration_test.path, integration_test.filename)\
							+ ' : Package added --> ' + integration_test.package.format_name())
			checked.append(integration_test)
			logger.info(self._project_log() + 'Integration test added --> ' + os.path.join(integration_test.path, integration_test.filename))
		self.integration_tests.tests = checked
		
	@_step
	def _configure(self, arg=None):
		ok = True
		objects = self.parser.parse()
		self.constants = objects['constants']
		if not self._check_repositories(objects):
			ok = False
		elif not self._check_artifacts(objects):
			ok = False
		elif not self._check_packages(objects):
			ok = False
		elif not self._check_preprocessors(objects):
			ok = False
		elif not self._check_builders(objects):
			ok = False
		elif not self._check_unit_tests(objects):
			ok = False
		elif not self._check_valgrind_tests(objects):
			ok = False
		elif not self._check_integration_tests(objects):
			ok = False
		if not self._check_subprojects(objects):
			ok = False
		else:
			for subproject in self.objects['subprojects']:
				if not subproject.configure():
					ok = False
		if self.step != 'deliver':
			self._set_workspace()
		return ok
		
	def configure(self, arg=None):
		return self._configure(arg)
	
# ============================================================================================================		

	@_step	
	def _build(self, arg=None):
		ok = True
		for subproject in self.objects['subprojects']:
			if not subproject._build():
				ok = False
		ok = self.preprocess.process() and self.build2.process() and self.artifacts_checks.process()
		if ok:
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
			if not subproject._test():
				ok = False
		return ok and self.unit_tests.process()

	def test(self, arg=None):
		if self.build():
			return self._test(arg)
			
# ============================================================================================================		

	@_step
	def _package(self, arg=None):
		ok = self.package2.process()
		for subproject in self.objects['subprojects']:
			if not subproject._package():
				ok = False
		return ok

	def package(self, arg=None):
		if self.test():
			return self._package(arg)
			
# ============================================================================================================		

	@_step
	def _verify(self, arg=None):
		ok = True
		for subproject in self.objects['subprojects']:
			if not subproject._verify():
				ok = False
		return ok and self.integration_tests.process()
		
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
		return ok and self.deploy2.process()
		
	def deploy(self, arg=None):
		if self.verify():
			return self._deploy(arg)
			
# ============================================================================================================		

	@_step
	def _deliver(self, path):
		ok = True
		for subproject in self.objects['subprojects']:
			if not subproject._deliver(path):
				ok = False
		self.deliver2.location = path
		return ok and self.deliver2.process()
		
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
		ok = self.retrieve2.process()
		for subproject in self.objects['subprojects']:
			if not subproject._retrieve():
				ok = False
		return ok

	def retrieve(self, arg=None):
		if self.configure():
			return self._retrieve(arg)
					
# ============================================================================================================		

	@_step
	def _parse(self, path, format='cppunit'):
		ok = True
		for report in [r for r in os.listdir(path) if r.endswith('.xml')]:
			test = Test('', path, report, [], format)
			test.errors = Reportable.parse_xml(format, os.path.join(path, report))
			if len(test.errors) > 0:
				test.status = Processible.STATUS['failure']
			else:
				test.status = Processible.STATUS['success']
			self.objects['unit_tests'].append(test)
		return ok
		
	def parse(self, arg=None):
		return self._parse(arg)
			
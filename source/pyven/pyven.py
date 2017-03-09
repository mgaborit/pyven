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
from pyven.steps.configure import Configure
from pyven.steps.preprocess import Preprocess
from pyven.steps.build import Build
from pyven.steps.artifacts_checks import ArtifactsChecks
from pyven.steps.unit_tests import UnitTests
from pyven.steps.package import PackageStep
from pyven.steps.integration_tests import IntegrationTests
from pyven.steps.install import Install
from pyven.steps.deploy import Deploy
from pyven.steps.retrieve import Retrieve
from pyven.steps.deliver import Deliver
from pyven.steps.clean import Clean

logger = logging.getLogger('global')

class Pyven:
	WORKSPACE = Workspace('workspace', 'workspace', os.path.join(os.getcwd(), 'pvn_workspace'))
	if pyven.constants.PLATFORM == 'windows':
		LOCAL_REPO = DirectoryRepo('local', 'file', os.path.join(os.environ.get('USERPROFILE'), 'pvn_repo'))
	elif pyven.constants.PLATFORM == 'linux':
		LOCAL_REPO = DirectoryRepo('local', 'file', os.path.join(os.environ.get('HOME'), 'pvn_repo'))
	if not os.path.isdir(LOCAL_REPO.url):
		os.makedirs(LOCAL_REPO.url)
		
	Step.LOCAL_REPO = LOCAL_REPO

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
		self.configure2 = Configure(self.path, self.verbose, self.pym)
		self.preprocess = Preprocess(self.path, self.verbose)
		self.build2 = Build(self.path, self.verbose, self.warning_as_error)
		self.artifacts_checks = ArtifactsChecks(self.path, self.verbose)
		self.unit_tests = UnitTests(self.path, self.verbose)
		self.package2 = PackageStep(self.path, self.verbose)
		self.integration_tests = IntegrationTests(self.path, self.verbose)
		self.install2 = Install(self.path, self.verbose)
		self.deploy2 = Deploy(self.path, self.verbose, self.release)
		self.retrieve2 = Retrieve(self.path, self.verbose)
		self.deliver2 = Deliver(self.path, self.verbose, '')
		self.clean2 = Clean(self.path, self.verbose)
		
	def reportables(self):
		reportables = []
		if self.step in ['verify', 'install', 'deploy']:
			if self.configure2.parser.checker.enabled():
				reportables.append(self.configure2.parser.checker)
			elif self.configure2.checker.enabled():
				reportables.append(self.configure2.checker)
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
				if self.install2.checker.enabled():
					reportables.append(self.install2.checker)
				if self.deploy2.checker.enabled():
					reportables.append(self.deploy2.checker)
		elif self.step in ['test', 'package']:
			if self.configure2.parser.checker.enabled():
				reportables.append(self.configure2.parser.checker)
			elif self.configure2.checker.enabled():
				reportables.append(self.configure2.checker)
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
			if self.configure2.parser.checker.enabled():
				reportables.append(self.configure2.parser.checker)
			elif self.configure2.checker.enabled():
				reportables.append(self.configure2.checker)
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
			if self.configure2.parser.checker.enabled():
				reportables.append(self.configure2.parser.checker)
			elif self.configure2.checker.enabled():
				reportables.append(self.configure2.checker)
			else:
				reportables.append(self.retrieve2.checker)
		elif self.step in ['deliver']:
			if self.configure2.parser.checker.enabled():
				reportables.append(self.configure2.parser.checker)
			elif self.configure2.checker.enabled():
				reportables.append(self.configure2.checker)
			else:
				reportables.append(self.deliver2.checker)
		elif self.step in ['parse']:
			reportables.extend(self.objects['unit_tests'])
		elif self.step in ['clean']:
			reportables.append(self.configure2.parser.checker)
			reportables.append(self.configure2.checker)
			reportables.append(self.clean2.checker)
		else:
			reportables.append(self.configure2.parser.checker)
			reportables.append(self.configure2.checker)
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
	@_step
	def _configure(self, arg=None):
		ok = self.configure2.process()
		for subproject in self.objects['subprojects']:
			if not subproject.configure():
				ok = False
		if ok:
			self.preprocess.tools = self.configure2.preprocessors
			self.build2.tools = self.configure2.builders
			self.artifacts_checks.artifacts = self.configure2.artifacts
			self.unit_tests.tests = self.configure2.unit_tests
			
			self.package2.artifacts = self.configure2.artifacts
			self.package2.packages = self.configure2.packages
			self.package2.repositories = self.configure2.repositories
			
			self.integration_tests.tests = self.configure2.integration_tests
			
			self.install2.artifacts = self.configure2.artifacts
			self.install2.packages = self.configure2.packages
			
			self.deploy2.artifacts = self.configure2.artifacts
			self.deploy2.packages = self.configure2.packages
			self.deploy2.repositories = self.configure2.repositories
			
			self.retrieve2.artifacts = self.configure2.artifacts
			self.retrieve2.packages = self.configure2.packages
			self.retrieve2.repositories = self.configure2.repositories
			
			self.deliver2.packages = self.configure2.packages
			self.deliver2.repositories = self.configure2.repositories
			
			self.clean2.preprocessors = self.configure2.preprocessors
			self.clean2.builders = self.configure2.builders
			
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
				Step.WORKSPACE.publish(artifact, artifact.file)
		return ok
		
	def build(self, arg=None):
		if self.configure():
			return self._build(arg)
			
# ============================================================================================================		

	def __test(self, tests, verbose=False):
		ok = True
		for test in tests:
			tic = time.time()
			if not test.process(verbose, Step.WORKSPACE):
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
		return ok and self.install2.process()
		
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
			if not subproject._clean():
				ok = False
		return ok and self.clean2.process()
	
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
			
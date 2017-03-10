import os, shutil, time
from lxml import etree

import pyven.constants
from pyven.logging.logger import Logger

from pyven.repositories.directory import DirectoryRepo
from pyven.repositories.workspace import Workspace
from pyven.reporting.reportable import Reportable
from pyven.processing.processible import Processible
from pyven.processing.tests.test import Test

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

class Pyven:	
	WORKSPACE = Workspace('workspace', 'workspace', os.path.join(os.getcwd(), 'pvn_workspace'))
	if not os.path.isdir(WORKSPACE.url):
		os.makedirs(WORKSPACE.url)
	Logger.get().info('Workspace set at : ' + WORKSPACE.url)

	if pyven.constants.PLATFORM == 'windows':
		LOCAL_REPO = DirectoryRepo('local', 'file', os.path.join(os.environ.get('USERPROFILE'), 'pvn_repo'))
	elif pyven.constants.PLATFORM == 'linux':
		LOCAL_REPO = DirectoryRepo('local', 'file', os.path.join(os.environ.get('HOME'), 'pvn_repo'))
	if not os.path.isdir(LOCAL_REPO.url):
		os.makedirs(LOCAL_REPO.url)

	Step.WORKSPACE = WORKSPACE
	Step.LOCAL_REPO = LOCAL_REPO

	STEPS = ['deliver', 'clean', 'retrieve', 'configure', 'preprocess', 'build', 'test', 'package', 'verify', 'install', 'deploy']
	UTILS = ['parse', 'aggregate']
	
	def __init__(self, step, verbose=False, warning_as_error=False, pym='pym.xml', release=False, path='', arguments={}):
		self.pym = pym
		self.path = path
		self.step = step
		self.verbose = verbose
		if self.verbose:
			Logger.get().info('Verbose mode enabled')
		self.release = release
		if self.release:
			Logger.get().info('Release mode enabled')
		self.warning_as_error = warning_as_error
		if self.warning_as_error:
			Logger.get().info('Warnings will be considered as errors')

		self.steps = []
		if step in Pyven.STEPS:
			self.steps.append(Configure(self.verbose, self.pym))
			step_id = Pyven.STEPS.index(step)
			if step_id > Pyven.STEPS.index('configure'):
				self.steps.append(Preprocess(self.verbose))
				
			if step_id > Pyven.STEPS.index('preprocess'):
				self.steps.append(Build(self.verbose, self.warning_as_error))
				self.steps.append(ArtifactsChecks(self.verbose))
				
			if step_id > Pyven.STEPS.index('build'):
				self.steps.append(UnitTests(self.verbose))
			
			if step_id > Pyven.STEPS.index('test'):
				self.steps.append(PackageStep(self.verbose))
			
			if step_id > Pyven.STEPS.index('package'):
				self.steps.append(IntegrationTests(self.verbose))
			
			if step_id > Pyven.STEPS.index('verify'):
				if step_id > Pyven.STEPS.index('install'):
					self.steps.append(Deploy(self.verbose, self.release))
			
				else:
					self.steps.append(Install(self.verbose))
			
			
			elif step_id < Pyven.STEPS.index('configure'):
				if step_id == Pyven.STEPS.index('deliver'):
					self.steps.append(Deliver(self.verbose, arguments['path']))
					
				elif step_id == Pyven.STEPS.index('clean'):
					self.steps.append(Clean(self.verbose))
				
				elif step_id == Pyven.STEPS.index('retrieve'):
					self.steps.append(Retrieve(self.verbose))
					
	def process(self):
		ok = True
		i = 0
		while ok and i < len(self.steps):
			if not self.steps[i].process():
				ok = False
			i += 1
		return ok

	def reportables(self):
		reportables = []
		if self.step in ['verify', 'install', 'deploy']:
			if self.configure.parser.checker.enabled():
				reportables.append(self.configure.parser.checker)
			elif self.configure.checker.enabled():
				reportables.append(self.configure.checker)
			else:
				reportables.extend(self.preprocess.tools)
				if self.preprocess.checker.enabled():
					reportables.append(self.preprocess.checker)
				reportables.extend(self.build.tools)
				if self.build.checker.enabled():
					reportables.append(self.build.checker)
				if self.artifacts_checks.checker.enabled():
					reportables.append(self.artifacts_checks.checker)
				reportables.extend(self.unit_tests.tests)
				if self.unit_tests.checker.enabled():
					reportables.append(self.unit_tests.checker)
				if self.package.checker.enabled():
					reportables.append(self.package.checker)
				reportables.extend(self.integration_tests.tests)
				if self.integration_tests.checker.enabled():
					reportables.append(self.integration_tests.checker)
				if self.install.checker.enabled():
					reportables.append(self.install.checker)
				if self.deploy.checker.enabled():
					reportables.append(self.deploy.checker)
		elif self.step in ['test', 'package']:
			if self.configure.parser.checker.enabled():
				reportables.append(self.configure.parser.checker)
			elif self.configure.checker.enabled():
				reportables.append(self.configure.checker)
			else:
				reportables.extend(self.preprocess.tools)
				if self.preprocess.checker.enabled():
					reportables.append(self.preprocess.checker)
				reportables.extend(self.build.tools)
				if self.build.checker.enabled():
					reportables.append(self.build.checker)
				if self.artifacts_checks.checker.enabled():
					reportables.append(self.artifacts_checks.checker)
				reportables.extend(self.unit_tests.tests)
				if self.unit_tests.checker.enabled():
					reportables.append(self.unit_tests.checker)
				if self.package.checker.enabled():
					reportables.append(self.package.checker)
		elif self.step in ['build']:
			if self.configure.parser.checker.enabled():
				reportables.append(self.configure.parser.checker)
			elif self.configure.checker.enabled():
				reportables.append(self.configure.checker)
			else:
				reportables.extend(self.preprocess.tools)
				if self.preprocess.checker.enabled():
					reportables.append(self.preprocess.checker)
				reportables.extend(self.build.tools)
				if self.build.checker.enabled():
					reportables.append(self.build.checker)
				if self.artifacts_checks.checker.enabled():
					reportables.append(self.artifacts_checks.checker)
		elif self.step in ['retrieve']:
			if self.configure.parser.checker.enabled():
				reportables.append(self.configure.parser.checker)
			elif self.configure.checker.enabled():
				reportables.append(self.configure.checker)
			else:
				reportables.append(self.retrieve.checker)
		elif self.step in ['deliver']:
			if self.configure.parser.checker.enabled():
				reportables.append(self.configure.parser.checker)
			elif self.configure.checker.enabled():
				reportables.append(self.configure.checker)
			else:
				reportables.append(self.deliver.checker)
		elif self.step in ['parse']:
			reportables.extend(self.unit_tests.tests)
		elif self.step in ['clean']:
			reportables.append(self.configure.parser.checker)
			reportables.append(self.configure.checker)
			reportables.append(self.clean.checker)
		else:
			reportables.append(self.configure.parser.checker)
			reportables.append(self.configure.checker)
		return reportables
	
# ============================================================================================================		
	def _parse(self, path, format='cppunit'):
		ok = True
		for report in [r for r in os.listdir(path) if r.endswith('.xml')]:
			test = Test('', path, report, [], format)
			test.errors = Reportable.parse_xml(format, os.path.join(path, report))
			if len(test.errors) > 0:
				test.status = Processible.STATUS['failure']
			else:
				test.status = Processible.STATUS['success']
			self.unit_tests.tests.append(test)
		return ok
		
	def parse(self, arg=None):
		return self._parse(arg)
			
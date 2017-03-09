import logging, os

from pyven.steps.step import Step
from pyven.checkers.checker import Checker
from pyven.parser.pym_parser import PymParser
from pyven.exceptions.exception import PyvenException

logger = logging.getLogger('global')

class Configure(Step):
	def __init__(self, path, verbose, pym):
		super(Configure, self).__init__(path, verbose)
		self.name = 'configure'
		self.checker = Checker('Configuration')
		self.parser = PymParser(pym)
		self.constants = {}
		self.subprojects = []
		self.repositories = {}
		self.artifacts = {}
		self.packages = {}
		self.preprocessors = []
		self.builders = []
		self.unit_tests = []
		self.valgrind_tests = []
		self.integration_tests = []

	@Step.error_checks
	def process(self):
		self.parser.parse_pym()
		self.constants = self.parser.parse_constants()
		return self._configure_subprojects()\
			and self._configure_repositories()\
			and self._configure_artifacts()\
			and self._configure_packages()\
			and self._configure_preprocessors()\
			and self._configure_builders()\
			and self._configure_unit_tests()\
			and self._configure_valgrind_tests()\
			and self._configure_integration_tests()
	
	def _replace_constants(self, str):
		for name, value in self.constants.items():
			str = str.replace('$('+name+')', value)
		return str

	def _configure_error_checks(function):
		def __intern(self):
			ok = True
			try:
				function(self)
			except PyvenException as e:
				self.checker.errors.append(e.args)
				for msg in e.args:
					logger.error(self.log_path() + msg)
				ok = False
			return ok
		return __intern
		
	@_configure_error_checks
	def _configure_subprojects(self):
		subprojects = self.parser.parse_subprojects()
		for subdirectory in subprojects:
			if not os.path.isdir(subdirectory):
				raise PyvenException('Subproject directory does not exist : ' + subdirectory)
			elif self.pym not in os.listdir(subdirectory):
				raise PyvenException('No ' + self.pym + ' file found at ' + subdirectory)
			else:
				#subproject = Pyven(step=self.step, verbose=self.verbose, warning_as_error=self.warning_as_error, pym=self.pym, path=os.path.join(self.path, subdirectory))
				self.subprojects.append(subdirectory)
				logger.info(self.log_path() + 'Added subproject --> ' + subdirectory)
	
	@_configure_error_checks
	def _configure_repositories(self):
		repositories = self.parser.parse_repositories()
		for repo in repositories:
			if repo.name == 'workspace' or repo.name == Step.LOCAL_REPO.name:
				raise PyvenException('Repository name reserved --> ' + repo.name + ' : ' + repo.url)
			else:
				if repo.name in self.repositories.keys():
					raise PyvenException('Repository already added --> ' + repo.name + ' : ' + repo.url)
				else:
					self.repositories[repo.name] = repo
					if repo.is_reachable():
						if repo.release:
							logger.info(self.log_path() + 'Release repository added --> ' + repo.name + ' : ' + repo.url)
						else:
							logger.info(self.log_path() + 'Repository added --> ' + repo.name + ' : ' + repo.url)
					else:
						logger.warning('Repository not accessible --> ' + repo.name + ' : ' + repo.url)
		
	@_configure_error_checks
	def _configure_artifacts(self):
		artifacts = self.parser.parse_artifacts()
		for artifact in artifacts:
			artifact.company = self._replace_constants(artifact.company)
			artifact.name = self._replace_constants(artifact.name)
			artifact.config = self._replace_constants(artifact.config)
			artifact.version = self._replace_constants(artifact.version)
			if not artifact.to_retrieve:
				artifact.file = self._replace_constants(artifact.file)
			if artifact.format_name() in self.artifacts.keys():
				raise PyvenException('Artifact already added --> ' + artifact.format_name())
			elif artifact.to_retrieve and artifact.repo not in self.repositories.keys() and artifact.repo not in [Step.LOCAL_REPO.name, 'workspace']:
				raise PyvenException('Artifact repository not declared --> ' + artifact.format_name() + ' : repo ' + artifact.repo)
			else:
				self.artifacts[artifact.format_name()] = artifact
				logger.info(self.log_path() + 'Artifact added --> ' + artifact.format_name())
				if not artifact.publish:
					logger.info(self.log_path() + 'Artifact ' + artifact.format_name() + ' --> publishment disabled')
		
	@_configure_error_checks
	def _configure_packages(self):
		packages = self.parser.parse_packages()
		for package in packages:
			package.company = self._replace_constants(package.company)
			package.name = self._replace_constants(package.name)
			package.config = self._replace_constants(package.config)
			package.version = self._replace_constants(package.version)
			package.delivery = self._replace_constants(package.delivery)
			items = []
			items.extend(package.items)
			package.items = []
			if package.format_name() in self.packages.keys():
				raise PyvenException('Package already added --> ' + package.format_name())
			elif package.to_retrieve and package.repo not in self.repositories.keys() and package.repo not in [Step.LOCAL_REPO.name, 'workspace']:
				raise PyvenException('Package repository not declared --> ' + package.format_name() + ' : repo ' + package.repo)
			else:
				for item in items:
					item = self._replace_constants(item)
					if item not in self.artifacts.keys():
						raise PyvenException('Package ' + package.format_name() + ' : Artifact not declared --> ' + item)
					else:
						package.items.append(self.artifacts[item])
						logger.info(self.log_path() + 'Package ' + package.format_name() + ' : Artifact added --> ' + item)
				self.packages[package.format_name()] = package
				logger.info(self.log_path() + 'Package added --> ' + package.format_name())
				if not package.publish:
					logger.info(self.log_path() + 'Package ' + package.format_name() + ' --> publishment disabled')
		
	@_configure_error_checks
	def _configure_preprocessors(self):
		preprocessors = self.parser.parse_preprocessors()
		checked = []
		for preprocessor in preprocessors:
			preprocessor.name = self._replace_constants(preprocessor.name)
			checked.append(preprocessor)
			logger.info(self.log_path() + 'Preprocessor added --> ' + preprocessor.type + ':' + preprocessor.name)
		self.preprocessors = checked
		
	@_configure_error_checks
	def _configure_builders(self):
		builders = self.parser.parse_builders()
		checked = []
		for builder in builders:
			builder.name = self._replace_constants(builder.name)
			checked.append(builder)
			logger.info(self.log_path() + 'Builder added --> ' + builder.type + ':' + builder.name)
		self.builders = checked
		
	@_configure_error_checks
	def _configure_unit_tests(self):
		unit_tests = self.parser.parse_unit_tests()
		checked = []
		for unit_test in unit_tests:
			checked.append(unit_test)
			logger.info(self.log_path() + 'Unit test added --> ' + os.path.join(unit_test.path, unit_test.filename))
		self.unit_tests = checked
		
	@_configure_error_checks
	def _configure_valgrind_tests(self):
		valgrind_tests = self.parser.parse_valgrind_tests()
		checked = []
		for valgrind_test in valgrind_tests:
			checked.append(valgrind_test)
			logger.info(self.log_path() + 'Valgrind test added --> ' + os.path.join(valgrind_test.path, valgrind_test.filename))
		self.valgrind_tests = checked
		
	@_configure_error_checks
	def _configure_integration_tests(self):
		integration_tests = self.parser.parse_integration_tests()
		checked = []
		for integration_test in integration_tests:
			integration_test.package = self._replace_constants(integration_test.package)
			if integration_test.package not in self.packages.keys():
				raise PyvenException('Integration test ' + os.path.join(integration_test.path, integration_test.filename)\
							+ ' : Package not declared --> ' + integration_test.package)
			else:
				integration_test.package = self.packages[integration_test.package]
				logger.info(self.log_path() + 'Integration test ' + os.path.join(integration_test.path, integration_test.filename)\
							+ ' : Package added --> ' + integration_test.package.format_name())
			checked.append(integration_test)
			logger.info(self.log_path() + 'Integration test added --> ' + os.path.join(integration_test.path, integration_test.filename))
		self.integration_tests = checked
		
from pyven.exceptions.exception import PyvenException
from pyven.repositories.directory import DirectoryRepo
from pyven.repositories.workspace import Workspace
from pyven.items.artifact import Artifact
from pyven.items.package import Package
from pyven.processing.tests.unit import UnitTest
from pyven.processing.tests.valgrind import ValgrindTest
from pyven.processing.tests.integration import IntegrationTest
from pyven.processing.tools.tool import Tool
from pyven.processing.tools.cmake import CMakeTool
from pyven.processing.tools.msbuild import MSBuildTool
from pyven.processing.tools.makefile import MakefileTool

class Factory:
	OBJECT_TYPES = ['repository', 'artifact', 'package', 'preprocessor', 'builder', 'unit_test', 'integration_test', 'valgrind_test']
	
	@staticmethod
	def _create_tool(node, project=None):
		type = node.get('type')
		if type is None:
			raise PyvenException('Missing tool type')
		if type not in Tool.TYPES:
			raise PyvenException('Wrong tool type : ' + type, 'Available tools : ' + str(Tool.TYPES))
		if type == Tool.TYPES[0]: 
			return CMakeTool(node)
		if type == Tool.TYPES[1] and project is not None:
			return MSBuildTool(node, project)
		if type == Tool.TYPES[2]: 
			return MakefileTool(node)
	
	@staticmethod
	def create(type, node, project=None):
		if type not in Factory.OBJECT_TYPES:
			raise PyvenException('Object type not known by the factory : ' + type)
		
		if type == Factory.OBJECT_TYPES[0] and project is None:
			return DirectoryRepo.from_node(node)
			
		elif type == Factory.OBJECT_TYPES[1] and project is None:
			return Artifact(node)
			
		elif type == Factory.OBJECT_TYPES[2] and project is None:
			return Package(node)
			
		elif type == Factory.OBJECT_TYPES[3] and project is None:
			return Factory._create_tool(node)
		
		elif type == Factory.OBJECT_TYPES[4] and project is None:
			return Factory._create_tool(node)
		
		elif type == Factory.OBJECT_TYPES[4] and project is not None:
			return Factory._create_tool(node, project)
		
		elif type == Factory.OBJECT_TYPES[5] and project is None:
			return UnitTest(node)
		
		elif type == Factory.OBJECT_TYPES[6] and project is None:
			return IntegrationTest(node)
			
		elif type == Factory.OBJECT_TYPES[7] and project is None:
			return ValgrindTest(node)
		
	@staticmethod
	def create_repo(name, type, url):
		if type == 'workspace':
			return Workspace(name, type, url)
		return DirectoryRepo(name, type, url)
import zipfile

def main():
	zf = zipfile.ZipFile('pvn.zip', mode='w')
	zf.write('__main__.py')
	zf.write('pyven/__init__.py')
	zf.write('pyven/pyven.py')
	zf.write('pyven/constants.py')
	
	zf.write('pyven/items/__init__.py')
	zf.write('pyven/items/item.py')
	zf.write('pyven/items/artifact.py')
	zf.write('pyven/items/package.py')
	
	zf.write('pyven/processing/__init__.py')
	zf.write('pyven/processing/processible.py')
	
	zf.write('pyven/processing/tools/__init__.py')
	zf.write('pyven/processing/tools/tool.py')
	zf.write('pyven/processing/tools/makefile.py')
	zf.write('pyven/processing/tools/msbuild.py')
	zf.write('pyven/processing/tools/cmake.py')
	
	zf.write('pyven/processing/tests/__init__.py')
	zf.write('pyven/processing/tests/test.py')
	zf.write('pyven/processing/tests/unit.py')
	zf.write('pyven/processing/tests/valgrind.py')
	zf.write('pyven/processing/tests/integration.py')
	
	zf.write('pyven/repositories/__init__.py')
	zf.write('pyven/repositories/repository.py')
	zf.write('pyven/repositories/directory.py')
	zf.write('pyven/repositories/workspace.py')
	
	zf.write('pyven/exceptions/__init__.py')
	zf.write('pyven/exceptions/exception.py')
	zf.write('pyven/exceptions/repository_exception.py')
	zf.write('pyven/exceptions/parser_exception.py')
	
	zf.write('pyven/reporting/__init__.py')
	zf.write('pyven/reporting/report.py')
	zf.write('pyven/reporting/reportable.py')
	zf.write('pyven/reporting/style.py')

	zf.write('pyven/parser/__init__.py')
	zf.write('pyven/parser/pym_parser.py')
	zf.write('pyven/parser/elements_parser.py')
	zf.write('pyven/parser/constants_parser.py')
	zf.write('pyven/parser/items_parser.py')
	zf.write('pyven/parser/artifacts_parser.py')
	zf.write('pyven/parser/packages_parser.py')
	zf.write('pyven/parser/tools_parser.py')
	zf.write('pyven/parser/msbuild_parser.py')
	zf.write('pyven/parser/cmake_parser.py')
	zf.write('pyven/parser/repositories_parser.py')
	zf.write('pyven/parser/directory_repo_parser.py')
	zf.write('pyven/parser/tests_parser.py')
	zf.write('pyven/parser/unit_tests_parser.py')
	zf.write('pyven/parser/valgrind_tests_parser.py')
	zf.write('pyven/parser/integration_tests_parser.py')
	
	zf.write('pyven/checkers/__init__.py')
	zf.write('pyven/checkers/checker.py')

if __name__ == '__main__':
	main()
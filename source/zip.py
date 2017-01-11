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
	
	zf.write('pyven/reporting/__init__.py')
	zf.write('pyven/reporting/report.py')
	zf.write('pyven/reporting/reportable.py')
	zf.write('pyven/reporting/style.py')

	zf.write('pyven/utils/__init__.py')
	zf.write('pyven/utils/factory.py')
	zf.write('pyven/utils/pym_parser.py')

if __name__ == '__main__':
	main()
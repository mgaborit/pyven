import zipfile

def main():
	zf = zipfile.ZipFile('pvn.zip', mode='w')
	zf.write('__main__.py')
	zf.write('pyven/__init__.py')
	zf.write('pyven/project.py')
	zf.write('pyven/item.py')
	zf.write('pyven/artifact.py')
	zf.write('pyven/package.py')
	zf.write('pyven/tool.py')
	zf.write('pyven/test.py')
	zf.write('pyven/repository.py')
	zf.write('pyven/exception.py')

if __name__ == '__main__':
	main()
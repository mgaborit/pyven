import sys

from pyven.project import Project

PYVEN_VERSION = '0.1.0'

def main(step):
	project = Project()
	
	if step == 'configure':
		project.configure()
		
	else:
		print 'Unknown step'
	
	
	
if __name__ == '__main__':
	main(sys.argv[1])
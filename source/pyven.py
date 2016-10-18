import sys
import logging

from pyven.project import Project

PYVEN_VERSION = '0.1.0'

logger = logging.getLogger('global')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s] %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
	
def main(step):
	project = Project()
	
	logger.info('Pyven command called for step ' + step)
	if step == 'configure':
		project.configure()
		
	elif step == 'build':
		project.configure()
		project.build()
		
	elif step == 'test':
		project.configure()
		project.build()
		project.test()
		
	elif step == 'package':
		project.configure()
		project.build()
		project.test()
		project.package()
		
	elif step == 'verify':
		project.verify()
		
	elif step == 'install':
		project.install()
		
	elif step == 'deploy':
		project.deploy()
		
	else:
		logger.error('Unknown step : ' + step)
	
	
	
if __name__ == '__main__':
	main(sys.argv[1])
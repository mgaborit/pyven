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
	
def main(args):
	if len(args) > 3:
		logger.error('Too many arguments passed to Pyven')

	if args[1] == '-v':
		logger.info('Verbose mode enabled')
		verbose = True
		step = args[2]
	else:
		logger.info('Verbose mode disabled')
		verbose = False
		step = args[1]
	
	project = Project(verbose)
	
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
		project.configure()
		project.build()
		project.test()
		project.package()
		project.verify()
		
	elif step == 'install':
		project.configure()
		project.build()
		project.test()
		project.package()
		project.verify()
		project.install()
		
	elif step == 'deploy':
		project.configure()
		project.build()
		project.test()
		project.package()
		project.verify()
		project.deploy()
		
	else:
		logger.error('Unknown step : ' + step)
	
	
	
if __name__ == '__main__':
	main(sys.argv)
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
		if not project.configure():
			logger.error('configure step ended with errors')
			sys.exit(1)
	
	elif step == 'build':
		if not project.configure():
			logger.error('configure step ended with errors')
			sys.exit(1)
		if not project.build():
			logger.error('build step ended with errors')
			sys.exit(1)
		
	elif step == 'test':
		if not project.configure():
			logger.error('configure step ended with errors')
			sys.exit(1)
		if not project.build():
			logger.error('build step ended with errors')
			sys.exit(1)
		if not project.test():
			logger.error('test step ended with errors')
			sys.exit(1)
		
	elif step == 'package':
		if not project.configure():
			logger.error('configure step ended with errors')
			sys.exit(1)
		if not project.build():
			logger.error('build step ended with errors')
			sys.exit(1)
		if not project.test():
			logger.error('test step ended with errors')
			sys.exit(1)
		if not project.package():
			logger.error('package step ended with errors')
			sys.exit(1)
		
	elif step == 'verify':
		if not project.configure():
			logger.error('configure step ended with errors')
			sys.exit(1)
		if not project.build():
			logger.error('build step ended with errors')
			sys.exit(1)
		if not project.test():
			logger.error('test step ended with errors')
			sys.exit(1)
		if not project.package():
			logger.error('package step ended with errors')
			sys.exit(1)
		if not project.verify():
			logger.error('verify step ended with errors')
			sys.exit(1)
		
	elif step == 'install':
		if not project.configure():
			logger.error('configure step ended with errors')
			sys.exit(1)
		if not project.build():
			logger.error('build step ended with errors')
			sys.exit(1)
		if not project.test():
			logger.error('test step ended with errors')
			sys.exit(1)
		if not project.package():
			logger.error('package step ended with errors')
			sys.exit(1)
		if not project.verify():
			logger.error('verify step ended with errors')
			sys.exit(1)
		if not project.install():
			logger.error('install step ended with errors')
			sys.exit(1)
		
	elif step == 'deploy':
		if not project.configure():
			logger.error('configure step ended with errors')
			sys.exit(1)
		if not project.build():
			logger.error('build step ended with errors')
			sys.exit(1)
		if not project.test():
			logger.error('test step ended with errors')
			sys.exit(1)
		if not project.package():
			logger.error('package step ended with errors')
			sys.exit(1)
		if not project.verify():
			logger.error('verify step ended with errors')
			sys.exit(1)
		if not project.deploy():
			logger.error('deploy step ended with errors')
			sys.exit(1)
		
	else:
		logger.error('Unknown step : ' + step)
		sys.exit(1)
	
	
	
if __name__ == '__main__':
	main(sys.argv)
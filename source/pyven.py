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
	if len(args) > 4:
		logger.error('Too many arguments passed to Pyven')

	verbose_arg = '-v'
	verbose = False
	if verbose_arg in args:
		if args.index(verbose_arg) > 1:
			logger.error('verbose option misplaced')
			sys.exit(1)
		logger.info('Verbose mode enabled')
		verbose = True
	
	if verbose:
		step_idx = 2
	else:
		step_idx = 1
		
	if not len(args) > step_idx:
		logger.error('Missing step call')
		sys.exit(1)
	
	possible_steps = ['configure', 'build', 'test', 'package', 'verify', 'install', 'deploy', 'deliver']
	if not args[step_idx] in possible_steps:
		logger.error('Invalid step call')
		sys.exit(1)
	
	step = args[step_idx]
	
	project = Project(verbose)
	
	logger.info('Pyven command called for step ' + step)
	if step == possible_steps[0]:
		if len(args) > step_idx + 1:
			logger.error('Too many arguments provided')
			sys.exit(1)
		if not project.configure():
			logger.error('configure step ended with errors')
			sys.exit(1)
	
	elif step == possible_steps[1]:
		if len(args) > step_idx + 1:
			logger.error('Too many arguments provided')
			sys.exit(1)
		if not project.configure():
			logger.error('configure step ended with errors')
			sys.exit(1)
		if not project.build():
			logger.error('build step ended with errors')
			sys.exit(1)
		
	elif step == possible_steps[2]:
		if len(args) > step_idx + 1:
			logger.error('Too many arguments provided')
			sys.exit(1)
		if not project.configure():
			logger.error('configure step ended with errors')
			sys.exit(1)
		if not project.build():
			logger.error('build step ended with errors')
			sys.exit(1)
		if not project.test():
			logger.error('test step ended with errors')
			sys.exit(1)
		
	elif step == possible_steps[3]:
		if len(args) > step_idx + 1:
			logger.error('Too many arguments provided')
			sys.exit(1)
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
		
	elif step == possible_steps[4]:
		if len(args) > step_idx + 1:
			logger.error('Too many arguments provided')
			sys.exit(1)
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
		
	elif step == possible_steps[5]:
		if len(args) > step_idx + 1:
			logger.error('Too many arguments provided')
			sys.exit(1)
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
		
	elif step == possible_steps[6]:
		if len(args) > step_idx + 1:
			logger.error('Too many arguments provided')
			sys.exit(1)
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
		
	elif step == possible_steps[7]:
		if len(args) > step_idx + 2:
			logger.error('Too many arguments provided')
			sys.exit(1)
		if len(args) < step_idx + 2:
			logger.error('missing path to delivery directory')
			sys.exit(1)
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
		if not project.deliver(args[step_idx + 1]):
			logger.error('deliver step ended with errors')
			sys.exit(1)
		
	else:
		logger.error('Unknown step : ' + step)
		sys.exit(1)
	
	
	
if __name__ == '__main__':
	main(sys.argv)
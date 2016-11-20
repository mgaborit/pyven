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

def hint():
	logger.error('Right syntax : "python pvn.py [-v] <step> [arg]"')
	logger.error("<step> values : " + str(Project.POSSIBLE_STEPS))

def main(args):
	tic = Project.tic()
	if len(args) > 4:
		logger.error('Too many arguments passed to Pyven')
		hint()
		sys.exit(1)
	logger.info('Pyven version : ' + PYVEN_VERSION)
	verbose_arg = '-v'
	verbose = False
	if verbose_arg in args:
		if args.index(verbose_arg) > 1:
			logger.error('verbose option misplaced')
			hint()
			sys.exit(1)
		logger.info('Verbose mode enabled')
		verbose = True
	
	if verbose:
		step_idx = 2
	else:
		step_idx = 1
		
	if not len(args) > step_idx:
		logger.error('Missing step call')
		hint()
		sys.exit(1)
	
	if not args[step_idx] in Project.POSSIBLE_STEPS:
		logger.error('Invalid step call')
		hint()
		sys.exit(1)
	
	step = args[step_idx]
	
	project = Project(PYVEN_VERSION, verbose)
	
	logger.info('Pyven command called for step ' + step)
	if step == Project.POSSIBLE_STEPS[0]:
		if len(args) > step_idx + 1:
			logger.error('Too many arguments provided')
			hint()
			sys.exit(1)
		if not project.configure():
			logger.error('STEP CONFIGURE : FAILED')
			sys.exit(1)
	
	elif step == Project.POSSIBLE_STEPS[1]:
		if len(args) > step_idx + 1:
			logger.error('Too many arguments provided')
			hint()
			sys.exit(1)
		if not project.configure():
			logger.error('STEP CONFIGURE : FAILED')
			sys.exit(1)
		if not project.build():
			logger.error('STEP BUILD : FAILED')
			sys.exit(1)
		
	elif step == Project.POSSIBLE_STEPS[2]:
		if len(args) > step_idx + 1:
			logger.error('Too many arguments provided')
			hint()
			sys.exit(1)
		if not project.configure():
			logger.error('STEP CONFIGURE : FAILED')
			sys.exit(1)
		if not project.build():
			logger.error('STEP BUILD : FAILED')
			sys.exit(1)
		if not project.test():
			logger.error('STEP TEST : FAILED')
			sys.exit(1)

	elif step == Project.POSSIBLE_STEPS[3]:
		if len(args) > step_idx + 1:
			logger.error('Too many arguments provided')
			hint()
			sys.exit(1)
		if not project.configure():
			logger.error('STEP CONFIGURE : FAILED')
			sys.exit(1)
		if not project.build():
			logger.error('STEP BUILD : FAILED')
			sys.exit(1)
		if not project.test():
			logger.error('STEP TEST : FAILED')
			sys.exit(1)
		if not project.package():
			logger.error('STEP PACKAGE : FAILED')
			sys.exit(1)
		
	elif step == Project.POSSIBLE_STEPS[4]:
		if len(args) > step_idx + 1:
			logger.error('Too many arguments provided')
			hint()
			sys.exit(1)
		if not project.configure():
			logger.error('STEP CONFIGURE : FAILED')
			sys.exit(1)
		if not project.build():
			logger.error('STEP BUILD : FAILED')
			sys.exit(1)
		if not project.test():
			logger.error('STEP TEST : FAILED')
			sys.exit(1)
		if not project.package():
			logger.error('STEP PACKAGE : FAILED')
			sys.exit(1)
		if not project.verify():
			logger.error('STEP VERIFY : FAILED')
			sys.exit(1)
		
	elif step == Project.POSSIBLE_STEPS[5]:
		if len(args) > step_idx + 1:
			logger.error('Too many arguments provided')
			hint()
			sys.exit(1)
		if not project.configure():
			logger.error('STEP CONFIGURE : FAILED')
			sys.exit(1)
		if not project.build():
			logger.error('STEP BUILD : FAILED')
			sys.exit(1)
		if not project.test():
			logger.error('STEP TEST : FAILED')
			sys.exit(1)
		if not project.package():
			logger.error('STEP PACKAGE : FAILED')
			sys.exit(1)
		if not project.verify():
			logger.error('STEP VERIFY : FAILED')
			sys.exit(1)
		if not project.install():
			logger.error('STEP INSTALL : FAILED')
			sys.exit(1)
		
	elif step == Project.POSSIBLE_STEPS[6]:
		if len(args) > step_idx + 1:
			logger.error('Too many arguments provided')
			hint()
			sys.exit(1)
		if not project.configure():
			logger.error('STEP CONFIGURE : FAILED')
			sys.exit(1)
		if not project.build():
			logger.error('STEP BUILD : FAILED')
			sys.exit(1)
		if not project.test():
			logger.error('STEP TEST : FAILED')
			sys.exit(1)
		if not project.package():
			logger.error('STEP PACKAGE : FAILED')
			sys.exit(1)
		if not project.verify():
			logger.error('STEP VERIFY : FAILED')
			sys.exit(1)
		if not project.deploy():
			logger.error('STEP DEPLOY : FAILED')
			sys.exit(1)
		
	elif step == Project.POSSIBLE_STEPS[7]:
		if len(args) > step_idx + 2:
			logger.error('Too many arguments provided')
			hint()
			sys.exit(1)
		if len(args) < step_idx + 2:
			logger.error('missing path to delivery directory')
			hint()
			sys.exit(1)
		if not project.configure():
			logger.error('STEP CONFIGURE : FAILED')
			sys.exit(1)
		if not project.build():
			logger.error('STEP BUILD : FAILED')
			sys.exit(1)
		if not project.test():
			logger.error('STEP TEST : FAILED')
			sys.exit(1)
		if not project.package():
			logger.error('STEP PACKAGE : FAILED')
			sys.exit(1)
		if not project.verify():
			logger.error('STEP VERIFY : FAILED')
			sys.exit(1)
		if not project.install():
			logger.error('STEP INSTALL : FAILED')
			sys.exit(1)
		if not project.deliver(args[step_idx + 1]):
			logger.error('STEP DELIVER : FAILED')
			sys.exit(1)
		
	elif step == Project.POSSIBLE_STEPS[8]:
		if len(args) > step_idx + 1:
			logger.error('Too many arguments provided')
			hint()
			sys.exit(1)
		if not project.configure():
			logger.error('STEP CONFIGURE : FAILED')
			sys.exit(1)
		if not project.clean():
			logger.error('STEP CLEAN : FAILED')
			sys.exit(1)
	else:
		logger.error('Unknown step : ' + step)
		sys.exit(1)
	
	toc = Project.toc()
	logger.info('Total process time : ' + str(round(toc - tic, 3)) + ' seconds')
	
if __name__ == '__main__':
	main(sys.argv)
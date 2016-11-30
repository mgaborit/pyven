
import sys
import logging

from pyven.exception import PyvenException

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
	
	try:
		logger.info('Pyven command called for step ' + step)
		if step == Project.POSSIBLE_STEPS[0]:
			if len(args) > step_idx + 1:
				logger.error('Too many arguments provided')
				hint()
				sys.exit(1)
			if not project.configure():
				raise PyvenException('STEP CONFIGURE : FAILED')
		
		elif step == Project.POSSIBLE_STEPS[1]:
			if len(args) > step_idx + 1:
				logger.error('Too many arguments provided')
				hint()
				sys.exit(1)
			if not project.configure():
				raise PyvenException('STEP CONFIGURE : FAILED')
			if not project.build():
				raise PyvenException('STEP BUILD : FAILED')
			project.write_report()
			
		elif step == Project.POSSIBLE_STEPS[2]:
			if len(args) > step_idx + 1:
				logger.error('Too many arguments provided')
				hint()
				sys.exit(1)
			if not project.configure():
				raise PyvenException('STEP CONFIGURE : FAILED')
			if not project.build():
				raise PyvenException('STEP BUILD : FAILED')
			if not project.test():
				raise PyvenException('STEP TEST : FAILED')
			project.write_report()

		elif step == Project.POSSIBLE_STEPS[3]:
			if len(args) > step_idx + 1:
				logger.error('Too many arguments provided')
				hint()
				sys.exit(1)
			if not project.configure():
				raise PyvenException('STEP CONFIGURE : FAILED')
			if not project.build():
				raise PyvenException('STEP BUILD : FAILED')
			if not project.test():
				raise PyvenException('STEP TEST : FAILED')
			if not project.package():
				raise PyvenException('STEP PACKAGE : FAILED')
			project.write_report()
			
		elif step == Project.POSSIBLE_STEPS[4]:
			if len(args) > step_idx + 1:
				logger.error('Too many arguments provided')
				hint()
				sys.exit(1)
			if not project.configure():
				raise PyvenException('STEP CONFIGURE : FAILED')
			if not project.build():
				raise PyvenException('STEP BUILD : FAILED')
			if not project.test():
				raise PyvenException('STEP TEST : FAILED')
			if not project.package():
				raise PyvenException('STEP PACKAGE : FAILED')
			if not project.verify():
				raise PyvenException('STEP VERIFY : FAILED')
			project.write_report()
			
		elif step == Project.POSSIBLE_STEPS[5]:
			if len(args) > step_idx + 1:
				logger.error('Too many arguments provided')
				hint()
				sys.exit(1)
			if not project.configure():
				raise PyvenException('STEP CONFIGURE : FAILED')
			if not project.build():
				raise PyvenException('STEP BUILD : FAILED')
			if not project.test():
				raise PyvenException('STEP TEST : FAILED')
			if not project.package():
				raise PyvenException('STEP PACKAGE : FAILED')
			if not project.verify():
				raise PyvenException('STEP VERIFY : FAILED')
			if not project.install():
				raise PyvenException('STEP INSTALL : FAILED')
			project.write_report()
			
		elif step == Project.POSSIBLE_STEPS[6]:
			if len(args) > step_idx + 1:
				logger.error('Too many arguments provided')
				hint()
				sys.exit(1)
			if not project.configure():
				raise PyvenException('STEP CONFIGURE : FAILED')
			if not project.build():
				raise PyvenException('STEP BUILD : FAILED')
			if not project.test():
				raise PyvenException('STEP TEST : FAILED')
			if not project.package():
				raise PyvenException('STEP PACKAGE : FAILED')
			if not project.verify():
				raise PyvenException('STEP VERIFY : FAILED')
			if not project.deploy():
				raise PyvenException('STEP DEPLOY : FAILED')
			project.write_report()
			
		elif step == Project.POSSIBLE_STEPS[7]:
			if len(args) > step_idx + 2:
				logger.error('Too many arguments provided')
				hint()
				sys.exit(1)
			if len(args) < step_idx + 2:
				logger.error('Missing path to delivery directory')
				hint()
				sys.exit(1)
			if not project.configure():
				raise PyvenException('STEP CONFIGURE : FAILED')
			if not project.build():
				raise PyvenException('STEP BUILD : FAILED')
			if not project.test():
				raise PyvenException('STEP TEST : FAILED')
			if not project.package():
				raise PyvenException('STEP PACKAGE : FAILED')
			if not project.verify():
				raise PyvenException('STEP VERIFY : FAILED')
			if not project.install():
				raise PyvenException('STEP INSTALL : FAILED')
			if not project.deliver(args[step_idx + 1]):
				raise PyvenException('STEP DELIVER : FAILED')
			project.write_report()
			
		elif step == Project.POSSIBLE_STEPS[8]:
			if len(args) > step_idx + 1:
				logger.error('Too many arguments provided')
				hint()
				sys.exit(1)
			if not project.configure():
				raise PyvenException('STEP CONFIGURE : FAILED')
			if not project.clean():
				raise PyvenException('STEP CLEAN : FAILED')
		else:
			logger.error('Unknown step : ' + step)
			hint()
			sys.exit(1)
	except PyvenException as e:
		for msg in e.args:
			logger.error(msg)
		sys.exit(1)
	
	toc = Project.toc()
	logger.info('Total process time : ' + str(round(toc - tic, 3)) + ' seconds')
	
if __name__ == '__main__':
	main(sys.argv)
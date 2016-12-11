import sys, logging, time

import pyven.constants
from pyven.exceptions.exception import PyvenException

from pyven.pyven import Pyven
from pyven.reporting.report import Report

logger = logging.getLogger('global')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s] %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

def hint():
	logger.error('Right syntax : "python pvn.py [-v] <step> [arg]"')
	logger.error("<step> values : " + str(Pyven.POSSIBLE_STEPS))

def main(args):
	tic = time.time()
	if len(args) > 4:
		logger.error('Too many arguments passed to Pyven')
		hint()
		sys.exit(1)
	logger.info('Pyven version : ' + pyven.constants.VERSION)
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
	
	if not args[step_idx] in Pyven.POSSIBLE_STEPS:
		logger.error('Invalid step call')
		hint()
		sys.exit(1)
	
	step = args[step_idx]
	
	project = Pyven(step, pyven.constants.VERSION, verbose)
	report = Report(project)
	
	try:
		logger.info('Pyven command called for step ' + step)
		if step == Pyven.POSSIBLE_STEPS[0]:
			if len(args) > step_idx + 1:
				logger.error('Too many arguments provided')
				hint()
				sys.exit(1)
			if not project.configure():
				raise PyvenException('STEP CONFIGURE : FAILED')
		
		elif step == Pyven.POSSIBLE_STEPS[1]:
			if len(args) > step_idx + 1:
				logger.error('Too many arguments provided')
				hint()
				sys.exit(1)
			if not project.configure():
				raise PyvenException('STEP CONFIGURE : FAILED')
			if not project.build():
				raise PyvenException('STEP BUILD : FAILED')
			
			
		elif step == Pyven.POSSIBLE_STEPS[2]:
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
			

		elif step == Pyven.POSSIBLE_STEPS[3]:
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
			
			
		elif step == Pyven.POSSIBLE_STEPS[4]:
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
			
			
		elif step == Pyven.POSSIBLE_STEPS[5]:
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
			
			
		elif step == Pyven.POSSIBLE_STEPS[6]:
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
			
			
		elif step == Pyven.POSSIBLE_STEPS[7]:
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
			
			
		elif step == Pyven.POSSIBLE_STEPS[8]:
			if len(args) > step_idx + 1:
				logger.error('Too many arguments provided')
				hint()
				sys.exit(1)
			if not project.configure():
				raise PyvenException('STEP CONFIGURE : FAILED')
			if not project.clean():
				raise PyvenException('STEP CLEAN : FAILED')
		elif step == Pyven.POSSIBLE_STEPS[9]:
			if len(args) > step_idx + 1:
				logger.error('Too many arguments provided')
				hint()
				sys.exit(1)
			if not project.configure():
				raise PyvenException('STEP CONFIGURE : FAILED')
			if not project.retrieve():
				raise PyvenException('STEP RETRIEVE : FAILED')
		else:
			logger.error('Unknown step : ' + step)
			hint()
			sys.exit(1)
	except PyvenException as e:
		for msg in e.args:
			logger.error(msg)
		sys.exit(1)
	finally:
		report.write()
		report.display()
	
	toc = time.time()
	logger.info('Total process time : ' + str(round(toc - tic, 3)) + ' seconds')
	
if __name__ == '__main__':
	main(sys.argv)
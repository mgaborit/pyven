import sys, logging, time, argparse

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

def main(args):
	tic = time.time()
	
	parser = argparse.ArgumentParser()
	parser.add_argument('--version', action='version', version='1.0.0')
	parser.add_argument('--verbose', '-v', action='store_true', help='Increases verbosity level')
	parser.add_argument('step', choices=pyven.constants.STEPS)
	parser.add_argument('path', nargs='?')
	args = parser.parse_args()
	
	project = Pyven(args.step, pyven.constants.VERSION, args.verbose)
	report = Report(project)
	try:
		if project.step != 'deliver' and args.path is not None:
			parser.error('Too many arguments provided')
	
		if project.step == 'configure':
			project.configure()
	
		if project.step == 'build':
			project.build()
	
		if project.step == 'test':
			project.test()
	
		if project.step == 'package':
			project.package()
	
		if project.step == 'verify':
			project.verify()
	
		if project.step == 'install':
			project.install()
	
		if project.step == 'deploy':
			project.deploy()
	
		if project.step == 'deliver':
			if args.path is not None:
				project.deliver(args.path)
			else:
				parser.error('Missing path to delivery directory')
	
		if project.step == 'clean':
			project.clean()
	
		if project.step == 'retrieve':
			project.retrieve()
	
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
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
	parser.add_argument('--display', '-d', action='store_true', help='display build report in the webbrowser right after build')
	parser.add_argument('--verbose', '-v', action='store_true', help='increase verbosity level')
	parser.add_argument('step', choices=pyven.constants.STEPS, help='pyven step to be achieved')
	parser.add_argument('path', nargs='?', help='path to the delivery directory (used with "deliver" step only)')
	args = parser.parse_args()
	
	project = Pyven(args.step, pyven.constants.VERSION, args.verbose)
	report = Report(project)
	try:
		ok = True
		if project.step != 'deliver' and args.path is not None:
			parser.error('Too many arguments provided')
	
		if project.step == 'configure':
			ok = project.configure()
	
		if project.step == 'build':
			ok = project.build()
			report.write()
	
		if project.step == 'test':
			ok = project.test()
			report.write()
	
		if project.step == 'package':
			ok = project.package()
			report.write()
	
		if project.step == 'verify':
			ok = project.verify()
			report.write()
	
		if project.step == 'install':
			ok = project.install()
			report.write()
	
		if project.step == 'deploy':
			ok = project.deploy()
			report.write()
	
		if project.step == 'deliver':
			if args.path is not None:
				ok = project.deliver(args.path)
			else:
				parser.error('Missing path to delivery directory')
				ok = False
	
		if project.step == 'clean':
			ok = project.clean()
	
		if project.step == 'retrieve':
			ok = project.retrieve()
	
		if not ok:
			raise PyvenException('Pyven build failed')
	
	except PyvenException as e:
		for msg in e.args:
			logger.error(msg)
		sys.exit(1)
	finally:
		if args.display:
			report.display()
	
		toc = time.time()
		logger.info('Total process time : ' + str(round(toc - tic, 3)) + ' seconds')
	
if __name__ == '__main__':
	main(sys.argv)
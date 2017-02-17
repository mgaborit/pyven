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
	parser.add_argument('--warning-as-error', '-wae', dest='warning_as_error', action='store_true', help='consider warnings as errors')
	parser.add_argument('--lines', '-l', dest='nb_lines', action='store', type=int, default=10, help='Number of errors/warnings to be displayed in the build report')
	parser.add_argument('--custom-pym', '-cp', dest='pym', action='store', type=str, default='pym.xml', help='Pym file name')
	parser.add_argument('--release', '-r', action='store_true', help='Enable deployment to release repositories')
	parser.add_argument('step', choices=pyven.constants.STEPS, help='pyven step to be achieved')
	parser.add_argument('path', nargs='?', help='path to the delivery directory (used with "deliver" step only)')
	args = parser.parse_args()
	
	project = Pyven(args.step, args.verbose, args.warning_as_error, args.pym, args.release)
	try:
		ok = True
		if project.step != 'deliver' and args.path is not None:
			parser.error('Too many arguments provided')
	
		if project.step == 'configure':
			ok = project.configure()
	
		if project.step == 'aggregate' and not args.display:
			Report.aggregate()
			
		if project.step == 'build':
			ok = project.build()
	
		if project.step == 'test':
			ok = project.test()
	
		if project.step == 'package':
			ok = project.package()
	
		if project.step == 'verify':
			ok = project.verify()
	
		if project.step == 'install':
			ok = project.install()
	
		if project.step == 'deploy':
			ok = project.deploy()
	
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
		if project.step not in ['aggregate', 'clean']:
			reports = [Report(project, args.nb_lines)]
			for subproject in project.objects['subprojects']:
				reports.append(Report(subproject, args.nb_lines))
			Report.clean()
			for report in reports:
				report.write()
			if args.display:
				Report.aggregate()
				Report.display()
	
		toc = time.time()
		logger.info('Total process time : ' + str(round(toc - tic, 3)) + ' seconds')
	
if __name__ == '__main__':
	main(sys.argv)
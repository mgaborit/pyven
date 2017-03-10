import sys, time, argparse
import pyven.constants

from pyven.exceptions.exception import PyvenException

from pyven.pyven import Pyven
from pyven.logging.logger import Logger
from pyven.reporting.html_utils import HTMLUtils

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
	parser.add_argument('step', choices=Pyven.STEPS + Pyven.UTILS, help='pyven step to be achieved')
	parser.add_argument('path', nargs='?', help='path to the delivery directory (used with "deliver" step only)')
	args = parser.parse_args()
	
	if args.step not in ['deliver', 'parse'] and args.path is not None:
		parser.error('Too many arguments provided')
	
	if args.step in ['deliver', 'parse'] and args.path is None:
		parser.error('Missing path argument for step ' + args.step)

	
	pyven = Pyven(args.step, args.verbose, args.warning_as_error, args.pym, args.release, arguments={'path' : args.path})
	try:
		ok = True
		if pyven.step == 'aggregate' and not args.display:
			HTMLUtils.aggregate()
		
		if pyven.step == 'parse':
			ok = pyven.parse(arguments['path'])
		
		else:
			ok = pyven.process()
		
		if not ok:
			raise PyvenException('Pyven build failed')
	
	except PyvenException as e:
		for msg in e.args:
			Logger.get().error(msg)
		sys.exit(1)
	finally:
		if pyven.step not in ['aggregate', 'clean']:
			pyven.report(args.nb_lines)
			if args.display:
				HTMLUtils.aggregate()
				HTMLUtils.display()
	
		toc = time.time()
		Logger.get().info('Total process time : ' + str(round(toc - tic, 3)) + ' seconds')
	
if __name__ == '__main__':
	main(sys.argv)
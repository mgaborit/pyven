import sys, time, argparse

from pyven.exceptions.exception import PyvenException

import pyven.constants as cst
from pyven.pyven import Pyven
from pyven.logging.logger import Logger

def main(args):
    tic = time.time()
    Logger.get().info('Pyven ' + cst.VERSION)
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version='1.0.0')
    parser.add_argument('--display', '-d', action='store_true', help='display build report in the webbrowser right after build')
    parser.add_argument('--verbose', '-v', action='store_true', help='increase verbosity level')
    parser.add_argument('--warning-as-error', '-wae', dest='warning_as_error', action='store_true', help='consider warnings as errors')
    parser.add_argument('--lines', '-l', dest='nb_lines', action='store', type=int, default=10, help='Number of errors/warnings to be displayed in the build report')
    parser.add_argument('--custom-pym', '-cp', dest='pym', action='store', type=str, default='pym.xml', help='pym file name')
    parser.add_argument('--release', '-r', action='store_true', help='enable deployment to release repositories')
    parser.add_argument('--overwrite', '-o', action='store_true', help='enable deployment to release repositories')
    parser.add_argument('--report-style', '-rs', dest='report_style', action='store', type=str, default='default', help='Sets the HTML report style')
    parser.add_argument('--multithread', '-m', dest='nb_threads', action='store', type=int, default=1, help='Number of threads for parallel build')
    parser.add_argument('step', choices=Pyven.STEPS + Pyven.UTILS, help='pyven step to be achieved')
    parser.add_argument('path', nargs='?', help='path to the delivery directory (used with "deliver" step only)')
    args = parser.parse_args()
    
    if args.step not in ['deliver', 'parse'] and args.path is not None:
        parser.error('Too many arguments provided')
    
    if args.step in ['deliver', 'parse'] and args.path is None:
        parser.error('Missing path argument for step ' + args.step)

    
    pvn = Pyven(args.step, args.verbose, args.warning_as_error, args.pym, args.release, args.overwrite, arguments={'path' : args.path}, nb_lines=args.nb_lines, nb_threads=args.nb_threads)
    try:
        ok = True
        if pvn.step == 'aggregate' and not args.display:
            pvn.report(args.report_style)
        
        if pvn.step == 'init':
            ok = pvn.init()
        
        else:
            ok = pvn.process()
        
        if not ok:
            raise PyvenException('Pyven build failed')
    
    except PyvenException as e:
        for msg in e.args:
            Logger.get().error(msg)
        sys.exit(1)
    finally:
        if pvn.step not in ['aggregate']:
            pvn.report(args.report_style)
            if args.display:
                pvn.display()
    
        toc = time.time()
        Logger.get().info('Total process time : ' + str(round(toc - tic, 3)) + ' seconds')
    
if __name__ == '__main__':
    main(sys.argv)
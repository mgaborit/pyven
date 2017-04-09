import zipfile, os
import pyven.constants

def zip_pvn():
    zf = zipfile.ZipFile(os.path.join(os.environ.get('PVN_HOME'), 'pvn_' + pyven.constants.VERSION + '.zip'), mode='w')
    zf.write('__main__.py')
    zf.write('pyven/__init__.py')
    zf.write('pyven/pyven.py')
    zf.write('pyven/project.py')
    zf.write('pyven/constants.py')
    
    zf.write('pyven/steps/__init__.py')
    zf.write('pyven/steps/step.py')
    zf.write('pyven/steps/configure.py')
    zf.write('pyven/steps/preprocess.py')
    zf.write('pyven/steps/build.py')
    zf.write('pyven/steps/postprocess.py')
    zf.write('pyven/steps/artifacts_checks.py')
    zf.write('pyven/steps/unit_tests.py')
    zf.write('pyven/steps/package.py')
    zf.write('pyven/steps/integration_tests.py')
    zf.write('pyven/steps/install.py')
    zf.write('pyven/steps/deploy.py')
    zf.write('pyven/steps/retrieve.py')
    zf.write('pyven/steps/deliver.py')
    zf.write('pyven/steps/clean.py')
    zf.write('pyven/steps/utils.py')
    
    zf.write('pyven/items/__init__.py')
    zf.write('pyven/items/item.py')
    zf.write('pyven/items/artifact.py')
    zf.write('pyven/items/package.py')
    
    zf.write('pyven/processing/__init__.py')
    zf.write('pyven/processing/processible.py')
    
    zf.write('pyven/processing/tools/__init__.py')
    zf.write('pyven/processing/tools/tool.py')
    zf.write('pyven/processing/tools/makefile.py')
    zf.write('pyven/processing/tools/msbuild.py')
    zf.write('pyven/processing/tools/cmake.py')
    zf.write('pyven/processing/tools/command.py')
    
    zf.write('pyven/processing/tests/__init__.py')
    zf.write('pyven/processing/tests/test.py')
    zf.write('pyven/processing/tests/unit.py')
    zf.write('pyven/processing/tests/valgrind.py')
    zf.write('pyven/processing/tests/integration.py')
    
    zf.write('pyven/repositories/__init__.py')
    zf.write('pyven/repositories/repository.py')
    zf.write('pyven/repositories/directory.py')
    zf.write('pyven/repositories/workspace.py')
    
    zf.write('pyven/exceptions/__init__.py')
    zf.write('pyven/exceptions/exception.py')
    zf.write('pyven/exceptions/repository_exception.py')
    zf.write('pyven/exceptions/parser_exception.py')
    
    zf.write('pyven/reporting/__init__.py')
    zf.write('pyven/reporting/html_utils.py')
    zf.write('pyven/reporting/reportable.py')
    zf.write('pyven/reporting/style.py')
    
    zf.write('pyven/reporting/content/__init__.py')
    zf.write('pyven/reporting/content/content.py')
    zf.write('pyven/reporting/content/line.py')
    zf.write('pyven/reporting/content/error.py')
    zf.write('pyven/reporting/content/warning.py')
    zf.write('pyven/reporting/content/status.py')
    zf.write('pyven/reporting/content/unknown.py')
    zf.write('pyven/reporting/content/success.py')
    zf.write('pyven/reporting/content/failure.py')
    zf.write('pyven/reporting/content/lines.py')
    zf.write('pyven/reporting/content/properties.py')
    zf.write('pyven/reporting/content/property.py')
    zf.write('pyven/reporting/content/title.py')
    zf.write('pyven/reporting/content/listing.py')
    zf.write('pyven/reporting/content/platform.py')
    zf.write('pyven/reporting/content/step.py')
    zf.write('pyven/reporting/content/reportable.py')
    zf.write('pyven/reporting/content/summary.py')

    zf.write('pyven/parser/__init__.py')
    zf.write('pyven/parser/pym_parser.py')
    zf.write('pyven/parser/elements_parser.py')
    zf.write('pyven/parser/constants_parser.py')
    zf.write('pyven/parser/items_parser.py')
    zf.write('pyven/parser/artifacts_parser.py')
    zf.write('pyven/parser/packages_parser.py')
    zf.write('pyven/parser/tools_parser.py')
    zf.write('pyven/parser/msbuild_parser.py')
    zf.write('pyven/parser/makefile_parser.py')
    zf.write('pyven/parser/cmake_parser.py')
    zf.write('pyven/parser/command_parser.py')
    zf.write('pyven/parser/repositories_parser.py')
    zf.write('pyven/parser/directory_repo_parser.py')
    zf.write('pyven/parser/tests_parser.py')
    zf.write('pyven/parser/unit_tests_parser.py')
    zf.write('pyven/parser/valgrind_tests_parser.py')
    zf.write('pyven/parser/integration_tests_parser.py')
    
    zf.write('pyven/checkers/__init__.py')
    zf.write('pyven/checkers/checker.py')
    
    zf.write('pyven/logging/__init__.py')
    zf.write('pyven/logging/logger.py')
    
    zf.write('pyven/utils/__init__.py')
    zf.write('pyven/utils/utils.py')
    zf.write('pyven/utils/parallelizer.py')
    zf.write('pyven/utils/pym_writer.py')
    
    zf.write('pyven/results/__init__.py')
    zf.write('pyven/results/results_parser.py')
    zf.write('pyven/results/logs_parser.py')
    zf.write('pyven/results/line_logs_parser.py')
    zf.write('pyven/results/block_logs_parser.py')
    zf.write('pyven/results/xml_parser.py')

if __name__ == '__main__':
    zip_pvn()
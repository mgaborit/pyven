import os

from pyven.exceptions.exception import PyvenException

VERSION = '0.1.0'
STEPS = ['configure', 'build', 'test', 'package', 'verify', 'install', 'deploy', 'deliver', 'clean', 'retrieve', 'aggregate', 'parse']

if os.name == 'nt':
	PLATFORM = 'windows'
elif os.name == 'posix':
	PLATFORM = 'linux'
else:
	raise PyvenException('Unsupported platform : ' + os.name, 'Supported platforms : windows, linux')
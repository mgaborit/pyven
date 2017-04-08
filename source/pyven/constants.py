import os

from pyven.exceptions.exception import PyvenException

MAJOR = 0
MINOR = 1
PATCH = 0
VERSION = '.'.join([str(MAJOR), str(MINOR), str(PATCH)])

if os.name == 'nt':
	PLATFORM = 'windows'
elif os.name == 'posix':
	PLATFORM = 'linux'
else:
	raise PyvenException('Unsupported platform : ' + os.name, 'Supported platforms : windows, linux')
	
STATUS = ['SUCCESS', 'FAILURE', 'UNKNOWN']
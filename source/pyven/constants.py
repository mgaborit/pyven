import os

from pyven.exceptions.exception import PyvenException

MAJOR = 0
MINOR = 2
PATCH = 7
VERSION = '.'.join([str(MAJOR), str(MINOR), str(PATCH)])

PLATFORMS = ['linux', 'windows']

if os.name == 'nt':
	PLATFORM = PLATFORMS[1]
elif os.name == 'posix':
	PLATFORM = PLATFORMS[0]
else:
	raise PyvenException('Unsupported platform : ' + os.name, 'Supported platforms : windows, linux')
	
STATUS = ['SUCCESS', 'FAILURE', 'UNKNOWN']
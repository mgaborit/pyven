import os

from pyven.exceptions.exception import PyvenException

VERSION = '0.1.0'

if os.name == 'nt':
	PLATFORM = 'windows'
elif os.name == 'posix':
	PLATFORM = 'linux'
else:
	raise PyvenException('Unsupported platform : ' + os.name, 'Supported platforms : windows, linux')
	
STATUS = ['SUCCESS', 'FAILURE', 'UNKNOWN']
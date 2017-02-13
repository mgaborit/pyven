from pyven.exceptions.exception import PyvenException

class ParserException(PyvenException):

	def __init__(self, message):
		super(ParserException, self).__init__(message)
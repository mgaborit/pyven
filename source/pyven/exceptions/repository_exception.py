from pyven.exceptions.exception import PyvenException

class RepositoryException(PyvenException):

	def __init__(self, message):
		super(RepositoryException, self).__init__(message)
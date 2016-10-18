import logging

logger = logging.getLogger('global')

# pym.xml 'artifact' node
class Artifact(object):

	def __init__(self, node):
		self.group = node.get('group')
		self.id = node.get('id')
		self.version = node.get('version')
		
	def is_internal(self):
		raise NotImplementedError('Invalid call to abstract method "is_internal"')
		
	def format_name(self):
		return self.group + ':' + self.id + ':' + self.version
		
	def factory(node):
		if node.get('scope') == "intern": return InternalArtifact(node)
		if node.get('scope') == "extern": return ExternalArtifact(node)
	factory = staticmethod(factory)
	
class InternalArtifact(Artifact):

	def __init__(self, node):
		super(InternalArtifact, self).__init__(node)
		self.file = node.find('file').text
		
	def is_internal(self):
		return True
		
class ExternalArtifact(Artifact):

	def __init__(self, node):
		super(ExternalArtifact, self).__init__(node)
		self.repository = node.find('repository').text
		
	def is_internal(self):
		return False
		
# pym.xml 'artifact' node
class Artifact(object):

	def __init__(self, node):
		self.group = node.get('group')
		self.id = node.get('id')
		self.version = node.get('version')
		
	def get(self):
		raise NotImplementedError('Invalid call')
		
	def factory(node):
		if node.get('scope') == "intern": return InternalArtifact(node)
		if node.get('scope') == "extern": return ExternalArtifact(node)
	factory = staticmethod(factory)
	
class InternalArtifact(Artifact):

	def __init__(self, node):
		super(InternalArtifact, self).__init__(node)
		self.file = node.find('file').text
		
	def get(self):
		return self.group, self.id, self.version, self.file
		
class ExternalArtifact(Artifact):

	def __init__(self, node):
		super(ExternalArtifact, self).__init__(node)
		self.repository = node.find('repository').text
		
	def get(self):
		return self.group, self.id, self.version, self.repository
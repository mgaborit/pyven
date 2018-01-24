import hashlib
import codecs

def hash(str, hash='ripemd160', encoding='utf-8'):
	h = hashlib.new(hash)
	h.update(str.encode(encoding))
	return h.hexdigest()
	
def str_to_file(str, filename):
	file = codecs.open(filename, 'w', 'utf-8')
	file.write(str)
	file.close()
	
def file_to_str(filename):
	file = codecs.open(filename, 'r', 'utf-8')
	str = file.read()
	file.close()
	return str
		
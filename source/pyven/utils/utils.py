import hashlib

def hash(str, hash='ripemd160', encoding='utf-8'):
	h = hashlib.new(hash)
	h.update(str.encode(encoding))
	return h.hexdigest()
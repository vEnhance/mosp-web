from hashlib import sha256

def normalize(s : str) -> str:
	return s.upper().replace(' ', '').strip()

def sha(s : str) -> str:
	return sha256(s.encode('UTF-8')).hexdigest()

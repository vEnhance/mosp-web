from hashlib import sha256


def normalize(s: str) -> str:
	return s.upper().replace(' ', '').strip()


def sha(s: str) -> str:
	return sha256(('MOSP_LIGHT_NOVEL_' + s).encode('UTF-8')).hexdigest()

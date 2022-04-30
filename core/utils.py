from hashlib import sha256
from typing import Optional

from django.http import HttpRequest


def normalize(s: str) -> str:
	return s.upper().replace(' ', '').strip()


def sha(s: str) -> str:
	return sha256(('MOSP_LIGHT_NOVEL_' + s).encode('UTF-8')).hexdigest()


def get_token_from_request(request: HttpRequest):  # -> Optional[Token]
	from .models import Token
	if not request.user.is_authenticated:
		return None

	token, _ = Token.objects.get_or_create(user=request.user)
	return token

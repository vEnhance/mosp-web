from hashlib import sha256
from typing import Optional

from django.http import HttpRequest


def normalize(s: str) -> str:
	return s.upper().replace(' ', '').strip()


def sha(s: str) -> str:
	return sha256(('MOSP_LIGHT_NOVEL_' + s).encode('UTF-8')).hexdigest()


def get_token_from_request(request: HttpRequest):  # -> Optional[Token]
	from .models import Token
	uuid = request.COOKIES.get('uuid', None)

	if request.user.is_authenticated and uuid is not None:
		# first get the attached token
		try:
			user_token: Optional[Token] = Token.objects.get(user=request.user, enabled=True)
		except Token.DoesNotExist:
			user_token = None
		try:
			uuid_token: Optional[Token] = Token.objects.get(uuid=uuid, enabled=True)
		except Token.DoesNotExist:
			uuid_token = None
		if user_token is None and uuid_token is None:
			return None
		elif user_token is None and uuid_token is not None:
			return uuid_token
		elif user_token is not None and uuid_token is None:
			return user_token
		elif user_token is not None and uuid_token is not None and user_token.pk == uuid_token.pk:
			return user_token  # either one okay
		else:
			return user_token
	elif uuid is not None:  # no authentication
		try:
			return Token.objects.get(uuid=uuid, enabled=True)
		except Token.DoesNotExist:
			return None
	elif request.user.is_authenticated:  # no cookie
		try:
			return Token.objects.get(user=request.user, enabled=True)
		except Token.DoesNotExist:
			return None
	else:
		return None

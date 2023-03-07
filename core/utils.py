from hashlib import sha256

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser, User


def normalize(s: str) -> str:
    return s.upper().replace(" ", "").strip()


def sha(s: str) -> str:
    return sha256(("MOSP_LIGHT_NOVEL_" + s).encode("UTF-8")).hexdigest()


def is_staff(user: AbstractBaseUser | AnonymousUser) -> bool:
    if not isinstance(user, User):
        return False
    return user.is_staff

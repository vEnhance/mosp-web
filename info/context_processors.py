from typing import Any, Dict

from django.http.request import HttpRequest

from .models import Page


def pages(request: HttpRequest) -> Dict[str, Any]:
    return {"pages": Page.objects.filter(listed=True)}

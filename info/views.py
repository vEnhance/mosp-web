from typing import Any

from django.contrib.auth.models import User
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.views.generic import DetailView, UpdateView

from .models import Page


# Create your views here.
class PageDetailView(DetailView):
	model = Page
	context_object_name = "page"

	def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
		page = self.get_object()
		assert isinstance(page, Page)
		assert page.published or isinstance(
			request.user, User
		) and request.user.is_staff, "no permission to view"
		return super().dispatch(request, *args, **kwargs)


class PageUpdateView(UpdateView):
	model = Page
	context_object_name = "page"
	fields = (
		'title',
		'content',
		'slug',
		'published',
		'listed',
	)

	def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
		assert isinstance(request.user, User) and request.user.is_staff, "no permission to edit"
		return super().dispatch(request, *args, **kwargs)

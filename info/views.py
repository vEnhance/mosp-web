from django.views.generic import DetailView, UpdateView
from . import models


# Create your views here.
class PageDetailView(DetailView):
	model = models.Page
	context_object_name = "page"

	def dispatch(self, request, *args, **kwargs):
		page: models.Page = self.get_object()  # type: ignore
		assert page.published or request.user.is_staff, "no permission to view"
		return super().dispatch(request, *args, **kwargs)


class PageUpdateView(UpdateView):
	model = models.Page
	context_object_name = "page"
	fields = (
		'title',
		'content',
		'slug',
		'published',
		'listed',
	)

	def dispatch(self, request, *args, **kwargs):
		page: models.Page = self.get_object()  # type: ignore
		assert request.user.is_staff, "no permission to edit"
		return super().dispatch(request, *args, **kwargs)

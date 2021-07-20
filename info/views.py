from django.views.generic import DetailView
from . import models

# Create your views here.
class PageDetailView(DetailView):
	model = models.Page
	context_object_name = "page"
	def dispatch(self, request, *args, **kwargs):
		page : models.Page = self.get_object() # type: ignore
		assert page.published or request.user.is_staff
		return super().dispatch(request, *args, **kwargs)

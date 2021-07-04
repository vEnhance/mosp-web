from django.views.generic import DetailView
from . import models

# Create your views here.
class PageDetailView(DetailView):
	model = models.Page
	context_object_name = "page"

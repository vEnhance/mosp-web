from django.urls import path

from . import views

urlpatterns = [
	path(r'<str:slug>', views.PageDetailView.as_view(), name='page-detail'),
	]

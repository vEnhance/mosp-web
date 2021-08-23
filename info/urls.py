from django.urls import path

from . import views

urlpatterns = [
	path(r'<str:slug>', views.PageDetailView.as_view(), name='page-detail'),
	path(r'<str:slug>/edit', views.PageUpdateView.as_view(), name='page-update'),
]

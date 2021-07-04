from django.urls import path

from . import views

urlpatterns = [
	path(r'<str:slug>', views.PageDetail.as_view(), name='page-detail'),
	]

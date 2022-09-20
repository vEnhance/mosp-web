from django.contrib import admin

from .models import Page

# Register your models here.


@admin.register(Page)
class PageAdmin(admin.ModelAdmin[Page]):
	list_display = (
		'title',
		'slug',
		'published',
		'listed',
	)
	list_display_links = (
		'title',
		'slug',
	)
	list_filter = (
		'published',
		'listed',
	)

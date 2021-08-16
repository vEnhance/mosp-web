from django.contrib import admin
from . import models

# Register your models here.


@admin.register(models.Page)
class PageAdmin(admin.ModelAdmin):
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

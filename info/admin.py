from django.contrib import admin
from . import models

# Register your models here.

@admin.register(models.Page)
class PageAdmin(admin.ModelAdmin):
	list_display = ('title', 'slug',)
	list_display_links = ('title', 'slug',)

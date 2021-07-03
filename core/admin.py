from django.contrib import admin
from . import models

# Register your models here.

@admin.register(models.Hunt)
class HuntAdmin(admin.ModelAdmin):
	list_display = ('number', 'name', 'start_date', 'visible')
	search_fields = ('name',)

@admin.register(models.Puzzle)
class PuzzleAdmin(admin.ModelAdmin):
	list_display = ('title', 'slug', 'is_meta', 'is_round',
			'force_visibility', 'unlock_date',
			'unlock_threshold', 'courage_bounty',)
	search_fields = ('id', 'name', 'parent__name', 'hunt__name')
	list_filter = ('is_round', 'is_meta', 'parent', 'hunt',)

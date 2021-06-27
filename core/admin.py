from django.contrib import admin
from . import models

# Register your models here.

@admin.register(models.Hunt)
class HuntAdmin(admin.ModelAdmin):
	list_display = ('number', 'name', 'start_date', 'visible')
	search_fields = ('name',)

@admin.register(models.Unit)
class UnitAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'hunt')
	search_fields = ('id', 'name', 'hunt__name')
	list_filter = ('hunt',)

@admin.register(models.Puzzle)
class PuzzleAdmin(admin.ModelAdmin):
	list_display = ('title', 'slug', 'icon', 'place',
			'force_visibility', 'unlock_date',
			'unlock_threshold', 'courage_bounty',)
	search_fields = ('id', 'name', 'round__name', 'hunt__name')
	list_filter = ('unit', 'unit__hunt')

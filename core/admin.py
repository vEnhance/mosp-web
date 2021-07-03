from django.contrib import admin
from . import models

# Register your models here.

@admin.register(models.Hunt)
class HuntAdmin(admin.ModelAdmin):
	list_display = ('number', 'name', 'start_date', 'visible')
	search_fields = ('name',)

@admin.register(models.Puzzle)
class PuzzleAdmin(admin.ModelAdmin):
	list_display = ('title', 'slug', 'is_meta', 'unlockable',)
	search_fields = ('id', 'name', 'unlockable__parent__name', 'unlockbale__hunt__name')
	list_filter = ('is_meta', 'unlockable__parent', 'unlockable__hunt',)

@admin.register(models.Round)
class RoundAdmin(admin.ModelAdmin):
	list_display = ('title', 'slug',)
	search_fields = ('id', 'name', 'slug', 'unlockable__parent__name', 'unlockbale__hunt__name')
	list_filter = ('unlockable__parent', 'unlockable__hunt',)

@admin.register(models.Unlockable)
class UnlockableAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'hunt', 'slug', 'parent',)
	search_fields = ('id', 'name', 'hunt', 'slug', 'parent__name', 'parent__slug',)
	list_filter = ('parent', 'hunt',)

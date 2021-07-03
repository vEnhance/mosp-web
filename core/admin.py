from django.contrib import admin
from . import models

# Register your models here.

@admin.register(models.Hunt)
class HuntAdmin(admin.ModelAdmin):
	list_display = ('volume_number', 'name', 'start_date', 'visible')
	search_fields = ('name',)

class SaltedAnswerInline(admin.TabularInline):
	model = models.SaltedAnswer
	fields = ('display_answer', 'salt', 'message',)
	extra = 2
class UnlockableInline(admin.TabularInline):
	model = models.Unlockable
	fields = ('name', 'hunt', 'slug',)
	extra = 2
class SolveInline(admin.TabularInline):
	model = models.Solve
	fields = ('unlockable', 'unlocked_on', 'solved_on',)
	extra = 0

@admin.register(models.Puzzle)
class PuzzleAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug', 'is_meta', 'unlockable',)
	search_fields = ('id', 'name', 'unlockable__parent__name', 'unlockbale__hunt__name')
	list_filter = ('is_meta', 'unlockable__parent', 'unlockable__hunt',)
	inlines = (SaltedAnswerInline,)

@admin.register(models.Round)
class RoundAdmin(admin.ModelAdmin):
	list_display = ('chapter_number', 'name', 'slug',)
	search_fields = ('id', 'name', 'slug', 'unlockable__parent__name', 'unlockbale__hunt__name')
	list_filter = ('unlockable__parent', 'unlockable__hunt',)

@admin.register(models.Unlockable)
class UnlockableAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'hunt', 'slug', 'parent',)
	search_fields = ('id', 'name', 'hunt', 'slug', 'parent__name', 'parent__slug',)
	list_filter = ('parent', 'hunt',)

@admin.register(models.Solve)
class SolveAdmin(admin.ModelAdmin):
	list_display = ('token', 'unlockable', 'unlocked_on', 'solved_on',)
	search_fields = ('token__name', 'unlockable__name',)
	list_filter = ('unlockable__hunt',)

@admin.register(models.Token)
class TokenAdmin(admin.ModelAdmin):
	list_display = ('uuid', 'name',)
	search_fields = ('uuid', 'name',)
	inlines = (SolveInline,)

@admin.register(models.SaltedAnswer)
class SaltedAnswerAdmin(admin.ModelAdmin):
	list_display = ('puzzle', 'salt',)

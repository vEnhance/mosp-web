from django.contrib import admin
from . import models

# Register your models here.

@admin.register(models.Hunt)
class HuntAdmin(admin.ModelAdmin):
	list_display = ('volume_number', 'name', 'start_date', 'visible')
	list_display_links = ('volume_number', 'name',)
	search_fields = ('name',)

class SaltedAnswerInline(admin.TabularInline):
	model = models.SaltedAnswer
	fields = ('display_answer', 'salt', 'message',)
	extra = 2
class UnlockableInline(admin.TabularInline):
	model = models.Unlockable
	fields = ('name', 'hunt', 'slug',)
	extra = 2
class AttemptInline(admin.TabularInline):
	model = models.Attempt
	fields = ('unlockable', 'solved_on',)
	extra = 0

@admin.register(models.Puzzle)
class PuzzleAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug', 'is_meta', 'unlockable',)
	list_display_links = ('name', 'slug',)
	search_fields = ('id', 'name', 'unlockable__parent__name', 'unlockbale__hunt__name')
	list_filter = ('is_meta', 'unlockable__hunt',)
	inlines = (SaltedAnswerInline,)

@admin.register(models.Round)
class RoundAdmin(admin.ModelAdmin):
	list_display = ('chapter_number', 'name', 'slug',)
	list_display_links = ('name', 'slug',)
	search_fields = ('id', 'name', 'slug', 'unlockable__parent__name', 'unlockbale__hunt__name')
	list_filter = ('unlockable__hunt',)

@admin.register(models.Unlockable)
class UnlockableAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug', 'icon', 'courage_bounty', 
			'force_visibility', 'parent_abbrv', 'prereqs_summary')
	list_display_links = ('name', 'slug')
	search_fields = ('id', 'name', 'hunt', 'slug', 'parent__name', 'parent__slug',)
	list_filter = ('hunt',)
	list_select_related = ('parent', 'hunt', 'round', 'parent__round',)

@admin.register(models.Attempt)
class AttemptAdmin(admin.ModelAdmin):
	list_display = ('token', 'unlockable', 'status',)
	list_display_links = ('token', 'unlockable',)
	search_fields = ('token__name', 'unlockable__name',)
	list_filter = ('unlockable__hunt',)

@admin.register(models.Token)
class TokenAdmin(admin.ModelAdmin):
	list_display = ('uuid', 'name',)
	search_fields = ('uuid', 'name',)
	inlines = (AttemptInline,)
	list_display_links = ('uuid', 'name',)

@admin.register(models.Solution)
class SolutionAdmin(admin.ModelAdmin):
	list_display = ('puzzle', 'post_solve_image_path', 'post_solve_image_alt',)
	search_fields = ('puzzle__name', 'post_solve_story', 'solution_text', 'author_notes',)

@admin.register(models.SaltedAnswer)
class SaltedAnswerAdmin(admin.ModelAdmin):
	list_display = ('puzzle', 'salt',)
	list_display_links = ('puzzle',)

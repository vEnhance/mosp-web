from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from . import models

# Register your models here.

@admin.register(models.Hunt)
class HuntAdmin(admin.ModelAdmin):
	list_display = ('volume_number', 'name', 'start_date', 'visible')
	list_display_links = ('volume_number', 'name',)
	search_fields = ('name',)

class SaltedAnswerInline(admin.TabularInline):
	model = models.SaltedAnswer
	fields = ('display_answer', 'salt', 'message', 'is_correct', 'is_canonical')
	extra = 2
class UnlockableInline(admin.TabularInline):
	model = models.Unlockable
	fields = ('name', 'hunt', 'slug',)
	extra = 2
class AttemptInline(admin.TabularInline):
	model = models.Attempt
	fields = ('unlockable', 'status',)
	extra = 0

@admin.register(models.Puzzle)
class PuzzleAdmin(MarkdownxModelAdmin):
	list_display = ('name', 'slug', 'is_meta', 'unlockable',)
	list_display_links = ('name', 'slug',)
	search_fields = ('id', 'name', 'slug',)
	list_filter = ('is_meta', 'unlockable__hunt',)
	inlines = (SaltedAnswerInline,)
	autocomplete_fields = ('unlockable',)

@admin.register(models.Round)
class RoundAdmin(MarkdownxModelAdmin):
	list_display = ('chapter_number', 'name', 'slug', 'show_chapter_number')
	list_display_links = ('name', 'slug',)
	search_fields = ('id', 'name', 'slug',)
	list_filter = ('unlockable__hunt',)
	autocomplete_fields = ('unlockable',)

@admin.register(models.Unlockable)
class UnlockableAdmin(MarkdownxModelAdmin):
	list_display = ('name', 'slug', '_icon', 'force_visibility',
			'sort_order', 'parent', 'prereqs_summary')
	list_display_links = ('name', 'slug')
	search_fields = ('id', 'name', 'slug',)
	list_filter = ('hunt', 'parent',)
	list_select_related = ('parent', 'hunt', 'round',)
	autocomplete_fields = ('hunt', 'parent', 'unlock_needs', 'on_solve_link_to',)

@admin.register(models.Attempt)
class AttemptAdmin(admin.ModelAdmin):
	list_display = ('token', 'unlockable', 'status',)
	list_display_links = ('token', 'unlockable',)
	search_fields = ('token__name', 'unlockable__name',)
	list_filter = ('unlockable__hunt',)
	autocomplete_fields = ('token', 'unlockable',)

@admin.register(models.Token)
class TokenAdmin(admin.ModelAdmin):
	list_display = ('uuid', 'name', 'enabled', 'permission',)
	search_fields = ('uuid', 'name', )
	inlines = (AttemptInline,)
	list_display_links = ('uuid', 'name',)
	autocomplete_fields = ('user',)

@admin.register(models.Solution)
class SolutionAdmin(MarkdownxModelAdmin):
	list_display = ('puzzle', 'post_solve_image_path', 'post_solve_image_alt',)
	search_fields = ('puzzle__name', 'post_solve_story', 'solution_text', 'author_notes',)
	autocomplete_fields = ('puzzle',)

@admin.register(models.SaltedAnswer)
class SaltedAnswerAdmin(admin.ModelAdmin):
	list_display = ('puzzle', 'salt', 'is_correct', 'is_canonical',)
	list_display_links = ('puzzle',)
	list_filter = ('is_correct', 'is_canonical',)
	autocomplete_fields = ('puzzle',)

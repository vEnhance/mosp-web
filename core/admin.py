from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from markdownx.admin import MarkdownxModelAdmin

from .models import Attempt, Hunt, Puzzle, Round, SaltedAnswer, Solution, TestSolveSession, Token, Unlockable  # NOQA


@admin.register(Hunt)
class HuntAdmin(admin.ModelAdmin):
	list_display = (
		'volume_number',
		'name',
		'start_date',
		'end_date',
		'visible',
	)
	list_display_links = (
		'volume_number',
		'name',
	)
	search_fields = ('name', )


class SaltedAnswerInline(admin.TabularInline):
	model = SaltedAnswer  # type: ignore
	fields = ('display_answer', 'salt', 'message', 'is_correct', 'is_canonical')
	extra = 2


class UnlockableInline(admin.TabularInline):
	model = Unlockable  # type: ignore
	fields = (
		'name',
		'hunt',
		'slug',
	)
	extra = 2


class AttemptInline(admin.TabularInline):
	model = Attempt  # type: ignore
	fields = (
		'unlockable',
		'status',
	)
	extra = 0


@admin.register(Puzzle)
class PuzzleAdmin(MarkdownxModelAdmin):
	list_display = (
		'name',
		'slug',
		'status_progress',
		'is_meta',
		'unlockable',
	)
	list_display_links = (
		'name',
		'slug',
	)
	search_fields = (
		'id',
		'name',
		'slug',
	)
	list_filter = ('is_meta', 'unlockable__hunt', 'status_progress')
	inlines = (SaltedAnswerInline, )
	autocomplete_fields = ('unlockable', )
	actions = ['mark_deferred', 'mark_published']

	@admin.action(description='Mark deferred')  # type: ignore
	def mark_deferred(self, request: HttpRequest, queryset: QuerySet[Puzzle]):
		queryset.update(status_progress=-1)

	@admin.action(description='Mark published')  # type: ignore
	def mark_published(self, request: HttpRequest, queryset: QuerySet[Puzzle]):
		queryset.update(status_progress=7)


@admin.register(TestSolveSession)
class TestSolveSessionAdmin(admin.ModelAdmin):
	list_display = ('uuid', 'expires', 'puzzle')
	search_fields = ('puzzle__name', )
	autocomplete_fields = ('puzzle', )


@admin.register(Round)
class RoundAdmin(MarkdownxModelAdmin):
	list_display = ('chapter_number', 'name', 'slug', 'show_chapter_number')
	list_display_links = (
		'name',
		'slug',
	)
	search_fields = (
		'id',
		'name',
		'slug',
	)
	list_filter = ('unlockable__hunt', )
	autocomplete_fields = ('unlockable', )


@admin.register(Unlockable)
class UnlockableAdmin(MarkdownxModelAdmin):
	list_display = (
		'name', 'slug', '_icon', 'force_visibility', 'sort_order', 'parent', 'prereqs_summary'
	)
	list_display_links = ('name', 'slug')
	search_fields = (
		'id',
		'name',
		'slug',
	)
	list_filter = (
		'hunt',
		'parent',
	)
	list_select_related = (
		'parent',
		'hunt',
		'round',
	)
	autocomplete_fields = (
		'hunt',
		'parent',
		'unlock_needs',
		'on_solve_link_to',
	)


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
	list_display = (
		'token',
		'unlockable',
		'status',
	)
	list_display_links = (
		'token',
		'unlockable',
	)
	search_fields = (
		'token__name',
		'unlockable__name',
	)
	list_filter = (
		'unlockable__hunt',
		'status',
		'token__permission',
	)
	autocomplete_fields = (
		'token',
		'unlockable',
	)


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
	list_display = (
		'uuid',
		'name',
		'enabled',
		'permission',
	)
	search_fields = (
		'uuid',
		'name',
	)
	inlines = (AttemptInline, )
	list_display_links = (
		'uuid',
		'name',
	)
	list_filter = ('permission', )
	autocomplete_fields = ('user', )


@admin.register(Solution)
class SolutionAdmin(MarkdownxModelAdmin):
	list_display = (
		'puzzle',
		'post_solve_image_path',
		'post_solve_image_alt',
	)
	search_fields = (
		'puzzle__name',
		'post_solve_story',
		'solution_text',
		'author_notes',
	)
	autocomplete_fields = ('puzzle', )


@admin.register(SaltedAnswer)
class SaltedAnswerAdmin(admin.ModelAdmin):
	list_display = (
		'puzzle',
		'salt',
		'is_correct',
		'is_canonical',
	)
	list_display_links = ('puzzle', )
	list_filter = (
		'is_correct',
		'is_canonical',
	)
	autocomplete_fields = ('puzzle', )

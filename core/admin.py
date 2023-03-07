from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin

from .models import Hunt, Puzzle, Round, SaltedAnswer, Solution, Unlockable  # NOQA


@admin.register(Hunt)
class HuntAdmin(admin.ModelAdmin[Hunt]):
    list_display = (
        "volume_number",
        "name",
        "start_date",
        "end_date",
        "visible",
    )
    list_display_links = (
        "volume_number",
        "name",
    )
    search_fields = ("name",)


class SaltedAnswerInline(admin.TabularInline[SaltedAnswer, Puzzle]):
    model = SaltedAnswer  # type: ignore
    fields = ("display_answer", "salt", "message", "is_correct", "is_canonical")
    extra = 2


@admin.register(Puzzle)
class PuzzleAdmin(MarkdownxModelAdmin):
    list_display = (
        "name",
        "slug",
        "is_meta",
        "unlockable",
    )
    list_display_links = (
        "name",
        "slug",
    )
    search_fields = (
        "id",
        "name",
        "slug",
    )
    list_filter = ("is_meta", "unlockable__hunt")
    inlines = (SaltedAnswerInline,)
    autocomplete_fields = ("unlockable",)


@admin.register(Round)
class RoundAdmin(MarkdownxModelAdmin):
    list_display = ("chapter_number", "name", "slug", "show_chapter_number")
    list_display_links = (
        "name",
        "slug",
    )
    search_fields = (
        "id",
        "name",
        "slug",
    )
    list_filter = ("unlockable__hunt",)
    autocomplete_fields = ("unlockable",)


@admin.register(Unlockable)
class UnlockableAdmin(MarkdownxModelAdmin):
    list_display = (
        "name",
        "slug",
        "_icon",
        "force_visibility",
        "sort_order",
        "parent",
        "prereqs_summary",
    )
    list_display_links = ("name", "slug")
    search_fields = (
        "id",
        "name",
        "slug",
    )
    list_filter = (
        "hunt",
        "parent",
    )
    list_select_related = (
        "parent",
        "hunt",
        "round",
    )
    autocomplete_fields = (
        "hunt",
        "parent",
        "unlock_needs",
        "on_solve_link_to",
    )


@admin.register(Solution)
class SolutionAdmin(MarkdownxModelAdmin):
    list_display = (
        "puzzle",
        "post_solve_image_path",
        "post_solve_image_alt",
    )
    search_fields = (
        "puzzle__name",
        "post_solve_story",
        "solution_text",
        "author_notes",
    )
    autocomplete_fields = ("puzzle",)


@admin.register(SaltedAnswer)
class SaltedAnswerAdmin(admin.ModelAdmin[SaltedAnswer]):
    list_display = (
        "puzzle",
        "salt",
        "is_correct",
        "is_canonical",
    )
    list_display_links = ("puzzle",)
    list_filter = (
        "is_correct",
        "is_canonical",
    )
    autocomplete_fields = ("puzzle",)

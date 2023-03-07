import random

from django.db import models
from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils import timezone
from markdownx.models import MarkdownxField

from .utils import normalize, sha


class Hunt(models.Model):
    volume_number = models.CharField(
        max_length=80,
        help_text="The volume number corresponding to this hunt",
        unique=True,
    )
    name = models.CharField(
        max_length=80, help_text="The name of this hunt", blank=True
    )
    authors = models.CharField(max_length=255, help_text="The credits for this hunt")

    start_date = models.DateTimeField(help_text="When the hunt can be started")
    end_date = models.DateTimeField(help_text="Show solutions after this date")
    visible = models.BooleanField(
        help_text="Whether the hunt is visible to people; "
        "use false if you're just testing",
        default=False,
    )

    thumbnail_path = models.CharField(
        max_length=80, help_text="Static argument for thumbnail image", blank=True
    )

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("round-unlockable-list", args=(self.volume_number,))

    @property
    def has_started(self) -> bool:
        return self.start_date < timezone.now()

    @property
    def has_ended(self) -> bool:
        return self.end_date < timezone.now()

    @property
    def active(self) -> bool:
        return self.has_started and not self.has_ended


class Unlockable(models.Model):
    hunt = models.ForeignKey(
        Hunt,
        help_text="The hunt this unlockable belongs to",
        on_delete=models.CASCADE,
    )
    parent = models.ForeignKey(
        "Round",
        help_text="Specifies a parent round",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )

    slug = models.SlugField(
        help_text="The slug for the unlockable",
    )
    name = models.CharField(
        max_length=80,
        help_text="The name for this unlockable (e.g. place on map)",
    )
    icon = models.CharField(
        max_length=5,
        help_text="Emoji for this unlockable",
        blank=True,
    )
    sort_order = models.SmallIntegerField(
        help_text="An integer to sort this unlockable by in the listing", default=50
    )

    story_only = models.BooleanField(
        help_text="If this unlockable is story only", default=False
    )
    intro_story_text = MarkdownxField(
        help_text="Markdown for the pre-entry story", blank=True
    )

    unlock_courage_threshold = models.IntegerField(
        default=0,
        help_text="Amount of courage needed to unlock",
    )
    unlock_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the unlockable can be unlocked",
    )
    unlock_needs = models.ForeignKey(
        "Unlockable",
        help_text="If this is nonempty, then unlock only when the target is done",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="blocking",
    )

    force_visibility = models.BooleanField(
        null=True,
        blank=True,
        help_text="Always show or hide",
        verbose_name="Show",
    )
    courage_bounty = models.IntegerField(
        help_text="Amount of courage obtained by solving",
        default=25,
        verbose_name="Bounty",
    )

    on_solve_link_to = models.ForeignKey(
        "Round",
        help_text="When solved, link to this round instead",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="redirected_by",
    )

    @property
    def is_puzzle(self) -> bool:
        return hasattr(self, "puzzle")

    @property
    def is_round(self) -> bool:
        return hasattr(self, "round")

    @property
    def prereqs_summary(self) -> str:
        s = f"{self.unlock_courage_threshold}💜"
        if self.unlock_date:
            s += "@" + self.unlock_date.isoformat()
        if self.unlock_needs:
            s += "/" + self.unlock_needs.slug
        s += f" ▶️▶️  (+{self.courage_bounty})"
        return s

    @property
    def _parent(self):
        if self.is_round:
            return f"Vol {self.hunt.volume_number}"
        elif self.parent is not None:
            return str(self.parent)
        else:
            return None

    @property
    def _icon(self) -> str:
        if self.story_only:
            return "Story"
        else:
            return self.icon or "?"

    def __str__(self) -> str:
        return self.slug

    def get_absolute_url(self):
        return reverse(
            "unlockable-detail",
            args=(self.hunt.volume_number, self.slug),
        )

    def get_editor_url(self):
        return reverse(
            "unlockable-update",
            args=(self.hunt.volume_number, self.slug),
        )

    class Meta:
        ordering = (
            "sort_order",
            "name",
        )


class Puzzle(models.Model):
    unlockable = models.OneToOneField(
        Unlockable,
        help_text="Associated unlockable for this puzzle",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    name = models.CharField(max_length=80)
    slug = models.SlugField(help_text="The slug for the puzzle")
    is_meta = models.BooleanField(help_text="Is this a metapuzzle?", default=False)

    flavor_text = MarkdownxField(
        help_text="Markdown for puzzle flavor text",
        blank=True,
    )
    content = MarkdownxField(
        help_text="Markdown for the puzzle content",
        blank=True,
    )
    puzzle_head = models.TextField(
        help_text="Extra HTML code for dynamic puzzles. "
        "Leave this blank for a standard 'static' puzzle.",
        blank=True,
    )
    salted_answers: QuerySet["SaltedAnswer"]

    @property
    def hunt_volume_number(self) -> str:
        if self.unlockable is not None:
            return self.unlockable.hunt.volume_number
        else:
            return "-"

    def get_absolute_url(self):
        return reverse("puzzle-detail", args=(self.hunt_volume_number, self.slug))

    def get_editor_url(self):
        return reverse("puzzle-update", args=(self.hunt_volume_number, self.slug))

    def get_solution_url(self):
        return reverse("solution-detail", args=(self.hunt_volume_number, self.slug))

    def get_parent_url(self) -> str:
        if self.unlockable is None:
            return "/"
        elif self.unlockable.parent is None:
            return self.unlockable.hunt.get_absolute_url()
        else:
            return self.unlockable.parent.get_absolute_url()

    def __str__(self) -> str:
        return self.name

    @property
    def target_hashes(self) -> list[str]:
        return [sa.hash for sa in self.salted_answers.all()]

    @property
    def answer(self) -> str:
        return self.salted_answers.get(is_canonical=True).display_answer


class Solution(models.Model):
    puzzle = models.OneToOneField(
        Puzzle, help_text="The puzzle this is a solution for", on_delete=models.CASCADE
    )
    post_solve_story = MarkdownxField(
        help_text="Markdown for the post-solve story",
        blank=True,
    )
    solution_text = MarkdownxField(
        help_text="Markdown for the puzzle solution",
        blank=True,
    )
    author_notes = MarkdownxField(
        help_text="Markdown for the author's notes",
        blank=True,
    )
    post_solve_image_path = models.CharField(
        max_length=240, help_text="Static path to the post-solve image", blank=True
    )
    post_solve_image_alt = models.CharField(
        max_length=240, help_text="Alt text for the post-solve image", blank=True
    )

    def get_absolute_url(self):
        return reverse(
            "solution-detail", args=(self.puzzle.hunt_volume_number, self.puzzle.slug)
        )

    def get_editor_url(self):
        return reverse(
            "solution-update", args=(self.puzzle.hunt_volume_number, self.puzzle.slug)
        )

    def __str__(self):
        return f"Solution to {self.puzzle.name}"


def _rand():
    return random.randrange(0, 10**4)


class SaltedAnswer(models.Model):
    puzzle = models.ForeignKey(
        Puzzle, on_delete=models.CASCADE, related_name="salted_answers"
    )
    display_answer = models.CharField(
        max_length=80,
        help_text="Display answer to the puzzle",
    )
    salt = models.SmallIntegerField(
        help_text="A random number from 0000 to 9999",
        default=_rand,
    )
    message = models.CharField(
        max_length=256,
        help_text="For partial answers, the nudge to provide solvers",
        blank=True,
    )
    is_correct = models.BooleanField(
        help_text="Make an answer correct; solver marks as correct if seen.",
        default=True,
    )
    is_canonical = models.BooleanField(
        help_text="Make this the answer printed by the website for solvers",
        default=True,
    )

    @property
    def hash(self) -> str:
        return sha(self.normalized_answer + str(self.salt))

    @property
    def normalized_answer(self) -> str:
        return normalize(self.display_answer)

    def equals(self, other: str):
        return self.normalized_answer == normalize(other)

    class Meta:
        unique_together = (
            "puzzle",
            "salt",
        )

    def __str__(self) -> str:
        return self.display_answer


class Round(models.Model):
    unlockable = models.OneToOneField(
        Unlockable,
        help_text="Associated unlockable for this round",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    name = models.CharField(max_length=80)
    chapter_number = models.CharField(
        max_length=80, help_text="Chapter identifier for the database", unique=True
    )
    show_chapter_number = models.BooleanField(
        help_text="Whether the chapter should be numbered on screen", default=True
    )
    slug = models.SlugField(help_text="The slug for the round", unique=True)
    thumbnail_path = models.CharField(
        max_length=80, help_text="Static argument for thumbnail image", blank=True
    )
    round_text = MarkdownxField(
        help_text="Markdown for content in the round page", blank=True
    )

    def get_absolute_url(self):
        return reverse("unlockable-list", args=(self.chapter_number,))

    def get_editor_url(self):
        return reverse("round-update", args=(self.chapter_number,))

    def __str__(self) -> str:
        return self.name

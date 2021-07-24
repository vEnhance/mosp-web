from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q, Max
from django.urls import reverse_lazy
from django.utils import timezone
from markdownx.models import MarkdownxField
from typing import Optional

import random
import re
import uuid

from .utils import sha, normalize

# Create your models here.

class Hunt(models.Model):
	volume_number = models.CharField(max_length = 80,
			help_text = "The volume number corresponding to this hunt",
			unique = True)
	name = models.CharField(max_length = 80,
			help_text = "The name of this hunt",
			blank = True)
	authors = models.CharField(max_length = 255,
			help_text = "The credits for this hunt")
	start_date = models.DateTimeField(
			help_text = "When the hunt can be started")
	visible = models.BooleanField(
			help_text = "Whether the hunt is visible to people; "
			"use false if you're just testing",
			default = False)
	allow_skip = models.BooleanField(
			help_text = "Whether to allow `skip puzzle`",
			default = False)
	thumbnail_path = models.CharField(max_length = 80,
			help_text = "Static argument for thumbnail image",
			blank = True)

	def __str__(self):
		return self.name
	def get_absolute_url(self):
		return reverse_lazy('round-unlockable-list', args=(self.volume_number,))
	def get_cheating_url(self):
		return reverse_lazy('round-unlockable-list-cheating', args=(self.volume_number,))

	def allow_cheat(self, token : 'Token'):
		if self.allow_skip is True:
			return True
		elif token.permission >= 40:
			return True
		return False

class Unlockable(models.Model):
	hunt = models.ForeignKey(Hunt,
			help_text = "The hunt this unlockable belongs to",
			on_delete = models.CASCADE,
			)
	parent = models.ForeignKey('Round',
			help_text = "Specifies a parent round",
			null = True, blank = True,
			on_delete = models.SET_NULL,
			related_name = 'children',
			)

	slug = models.SlugField(
			help_text = "The slug for the unlockable",
			)
	name = models.CharField(max_length=80,
			help_text = "The name for this unlockable (e.g. place on map)",
			)
	icon = models.CharField(max_length = 5,
			help_text = "Emoji for this unlockable",
			blank = True,
			)
	sort_order = models.SmallIntegerField(
			help_text = "An integer to sort this unlockable by in the listing",
			default = 50)

	story_only = models.BooleanField(
			help_text = "If this unlockable is story only",
			default = False)
	intro_story_text = MarkdownxField(
			help_text = "Markdown for the pre-entry story",
			blank = True)

	unlock_courage_threshold = models.IntegerField(
			default = 0,
			help_text = "Amount of courage needed to unlock",
			)
	unlock_date = models.DateTimeField(
			null = True,
			blank = True,
			help_text = "When the unlockable can be unlocked",
			)
	unlock_needs = models.ForeignKey('Unlockable',
			help_text = "If this is nonempty, "
				"then unlock only when the target is done",
			null = True, blank = True,
			on_delete = models.SET_NULL,
			related_name = 'blocking',
			)

	force_visibility = models.BooleanField(
			null = True,
			blank = True,
			help_text = "Always show or hide",
			verbose_name = "Show",
			)
	courage_bounty = models.IntegerField(
			help_text = "Amount of courage obtained by solving",
			default = 25,
			verbose_name = "Bounty",
			)

	on_solve_link_to = models.ForeignKey('Round',
			help_text = "When solved, link to this round instead",
			null = True, blank = True,
			on_delete = models.SET_NULL,
			related_name = 'redirected_by')

	def get_finished_url(self, token) -> str:
		if self.on_solve_link_to is None:
			if self.parent is None:
				return self.hunt.get_absolute_url()
			else:
				return self.parent.get_absolute_url()
		elif self.on_solve_link_to.unlockable is None:
			return self.hunt.get_absolute_url() # wtf
		elif token.has_unlocked(self.on_solve_link_to.unlockable):
			return self.on_solve_link_to.unlockable.get_absolute_url()
		else:
			return self.on_solve_link_to.get_absolute_url()

	@property
	def is_puzzle(self) -> bool:
		return hasattr(self, 'puzzle')
	@property
	def is_round(self) -> bool:
		return hasattr(self, 'round')
	@property
	def prereqs_summary(self):
		s = f'{self.unlock_courage_threshold}💜'
		if self.unlock_date:
			s += '@' + self.unlock_date.isoformat()
		if self.unlock_needs:
			s += '/' + self.unlock_needs.slug
		s += f' ▶️▶️  (+{self.courage_bounty})'
		return s
	@property
	def _parent(self):
		if self.is_round:
			return f'Vol {self.hunt.volume_number}'
		elif self.parent is not None:
			return str(self.parent)
		else:
			return None
	@property
	def _icon(self):
		if self.story_only:
			return 'Story'
		else:
			return self.icon or '?'

	def __str__(self):
		return self.slug
	def get_absolute_url(self):
		return reverse_lazy('unlockable-detail',
				args=(self.hunt.volume_number, self.slug,))
	def get_editor_url(self):
		return reverse_lazy('unlockable-update',
				args=(self.hunt.volume_number, self.slug,))

	class Meta:
		ordering = ('sort_order', 'name',)

class Puzzle(models.Model):
	unlockable = models.OneToOneField(Unlockable,
			help_text = "Associated unlockable for this puzzle",
			null = True, blank = True,
			on_delete = models.SET_NULL)
	name = models.CharField(max_length = 80)
	slug = models.SlugField(
			help_text = "The slug for the puzzle",
			)
	is_meta = models.BooleanField(
			help_text = "Whether this is a metapuzzle",
			default = False)
	flavor_text = MarkdownxField(
			help_text = "Markdown for puzzle flavor text",
			blank = True,
			)
	content = MarkdownxField(
			help_text = "Markdown for the puzzle content",
			blank = True,
			)
	puzzle_head = models.TextField(
			help_text = "Extra HTML to include in HTML header",
			blank = True,
			)
	@property
	def hunt_volume_number(self):
		return self.unlockable.hunt.volume_number if self.unlockable is not None else '-'
	def get_absolute_url(self):
		return reverse_lazy('puzzle-detail',
				args=(self.hunt_volume_number, self.slug,))
	def get_editor_url(self):
		return reverse_lazy('puzzle-update',
				args=(self.hunt_volume_number, self.slug,))
	def get_solution_url(self):
		return reverse_lazy('solution-detail',
				args=(self.hunt_volume_number, self.slug,))
	def get_cheating_url(self):
		return reverse_lazy('solution-detail-cheating',
				args=(self.hunt_volume_number, self.slug,))
	def get_parent_url(self):
		return self.unlockable.parent.get_absolute_url()
	def __str__(self):
		return self.name
	@property
	def target_hashes(self):
		return [sa.hash for sa in self.salted_answers.all()] # type: ignore
	@property
	def answer(self):
		return self.salted_answers.get(is_canonical=True).display_answer # type: ignore

class Solution(models.Model):
	puzzle = models.OneToOneField(Puzzle,
			help_text = "The puzzle this is a solution for",
			on_delete = models.CASCADE
			)
	post_solve_story = MarkdownxField(
			help_text = "Markdown for the post-solve story",
			blank = True,
			)
	solution_text = MarkdownxField(
			help_text = "Markdown for the puzzle solution",
			blank = True,
			)
	author_notes = MarkdownxField(
			help_text = "Markdown for the author's notes",
			blank = True,
			)
	post_solve_image_path = models.CharField(max_length = 240,
			help_text = "Static path to the post-solve image",
			blank = True
			)
	post_solve_image_alt = models.CharField(max_length = 240,
			help_text = "Alt text for the post-solve image",
			blank = True
			)
	def get_absolute_url(self):
		return reverse_lazy('solution-detail', args=(
			self.puzzle.hunt_volume_number, self.puzzle.slug,))
	def get_editor_url(self):
		return reverse_lazy('solution-update', args=(
			self.puzzle.hunt_volume_number, self.puzzle.slug,))
	def __str__(self):
		return f"Solution to {self.puzzle.name}"

def _rand():
	return random.randrange(0, 10**4)
class SaltedAnswer(models.Model):
	puzzle = models.ForeignKey(Puzzle,
			on_delete = models.CASCADE,
			related_name = 'salted_answers')
	display_answer = models.CharField(max_length = 80,
			help_text = "Display answer to the puzzle",
			)
	salt = models.SmallIntegerField(
			help_text = "A random number from 0000 to 9999",
			default = _rand,
			)
	message = models.CharField(max_length=256,
			help_text = "For partial answers, the nudge to provide solvers",
			blank = True)
	is_correct = models.BooleanField(
			help_text = "Make an answer correct; solver marks as correct if seen.",
			default = True)
	is_canonical = models.BooleanField(
			help_text = "Make this the answer printed by the website for solvers",
			default = True)
	@property
	def hash(self) -> str:
		return sha(self.normalized_answer + str(self.salt))
	@property
	def normalized_answer(self) -> str:
		return normalize(self.display_answer)
	def equals(self, other : str):
		return self.normalized_answer == normalize(other)
	class Meta:
		unique_together = ('puzzle', 'salt',)
	def __str__(self):
		return self.display_answer

class Round(models.Model):
	unlockable = models.OneToOneField(Unlockable,
			help_text = "Associated unlockable for this round",
			null = True, blank = True,
			on_delete = models.SET_NULL)
	name = models.CharField(max_length = 80)
	chapter_number = models.CharField(max_length = 80,
			help_text = "Chapter identifier for the database",
			unique = True)
	show_chapter_number = models.BooleanField(
			help_text = "Whether the chapter should be numbered on screen",
			default = True)
	slug = models.SlugField(
			help_text = "The slug for the round",
			unique = True,
			)
	thumbnail_path = models.CharField(max_length = 80,
			help_text = "Static argument for thumbnail image",
			blank = True)
	round_text = MarkdownxField(
			help_text = "Markdown for content in the round page",
			blank = True)
	def get_absolute_url(self):
		return reverse_lazy('unlockable-list', args=(self.chapter_number,))
	def get_editor_url(self):
		return reverse_lazy('round-update', args=(self.chapter_number,))
	def get_cheating_url(self):
		return reverse_lazy('unlockable-list-cheating', args=(self.chapter_number,))
	def __str__(self):
		return self.name


class Hint(models.Model):
	cost = models.PositiveSmallIntegerField(
			help_text = "The cost of the hint (patience)")
	question = models.CharField(max_length = 120,
			help_text = "The question that the hint is for")
	answer = models.CharField(max_length = 120,
			help_text = "The content of the hint")
	minutes_until_unlock = models.PositiveSmallIntegerField(
			help_text = "Minutes until the hint is visible")

class Attempt(models.Model):
	token = models.ForeignKey('Token',
			help_text = "The token this attempt is for",
			on_delete = models.CASCADE)
	unlockable = models.ForeignKey(Unlockable,
			on_delete = models.CASCADE)
	status = models.SmallIntegerField(
			choices = (
				(-1, "Found"),
				( 0, "Unlocked"),
				( 1, "Solved"),
			), default = -1)
	found_on = models.DateTimeField(
			help_text = "When the unlockable is found",
			blank = True, null = True
			)
	unlocked_on = models.DateTimeField(
			help_text = "When the unlockable is unlocked",
			blank = True, null = True
			)
	solved_on = models.DateTimeField(
			help_text = "When the unlockable is unlocked",
			blank = True, null = True
			)
	def save(self, *args, **kwargs):
		if self.status >= -1 and self.found_on is None:
			self.found_on = timezone.now()
		if self.status >= 0 and self.unlocked_on is None:
			self.unlocked_on = timezone.now()
		if self.status >= 1 and self.unlocked_on is None:
			self.solved_on = timezone.now()
		super().save(*args, **kwargs)
	def __str__(self):
		verb : str = self.get_status_display().lower() # type: ignore
		return f'{self.token.pk} {verb}'
	class Meta:
		unique_together = ('token', 'unlockable',)

class Token(models.Model):
	uuid = models.UUIDField(
			primary_key = True,
			default = uuid.uuid4,
			editable = False)
	user = models.OneToOneField(User,
			on_delete = models.SET_NULL,
			null = True, blank = True)
	name = models.CharField(max_length = 128,
			help_text = "Who are you?")
	reduced_name = models.CharField(max_length = 128,
			help_text = "Name with only [a-z0-9] characters.")
	permission = models.PositiveSmallIntegerField(
			help_text = "Whether this token has any elevated permissions",
			choices = (
				(0, "Normal user"),
				(20, "Testsolver"),
				(40, "Bestsolver"),
				(60, "Editor"),
				(80, "Admin"),
				(100, "Evan Chen"),
			), default = 0)
	enabled = models.BooleanField(
			   help_text = "Turn off to prevent the token from being used",
			   default = True,
			   )
	hints_obtained = models.ManyToManyField(Hint,
			help_text = "Hints purchased by this token",
			blank = True)
	attempts = models.ManyToManyField(Unlockable, through=Attempt,
			help_text = "Attempts attached to this token")

	@staticmethod
	def reduce(s : str):
		return re.sub(r'\W+', '', s.lower())
	def save(self, *args, **kwargs):
		self.reduced_name = self.reduce(self.name)
		super().save(*args, **kwargs)

	def __str__(self):
		return self.name
	def get_absolute_url(self):
		return reverse_lazy('token-detail', args=(self.uuid,))

	@property
	def firstname(self):
		if not ' ' in self.name:
			return self.name
		return self.name[:self.name.index(' ')]

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._courage = Attempt.objects.filter(token=self, status=1)\
				.aggregate(courage = models.Sum('unlockable__courage_bounty'))['courage']\
				or 0

	def get_courage(self):
		return self._courage

	def can_unlock(self, u : Unlockable) -> bool:
		if u.unlock_date is not None:
			if u.unlock_date > timezone.now():
				return False
		if u.unlock_needs is not None:
			if hasattr(u, 'rstatus'):
				if u.rstatus != 1: # type: ignore
					return False
			else:
				if not self.has_solved(u.unlock_needs):
					return False
		return self.get_courage() >= u.unlock_courage_threshold
	@property
	def omniscient(self):
		return self.permission >= 40

	def can_view(self, u : Optional[Unlockable]) -> bool:
		if u is None:
			return self.omniscient
		if u.force_visibility is True:
			return True
		elif u.force_visibility is False:
			return False
		else:
			return self.can_unlock(u)
	def has_found(self, u : Optional[Unlockable]) -> bool:
		if u is None:
			return self.omniscient
		if hasattr(u, 'ustatus'):
			return u.ustatus is not None # type: ignore
		return Attempt.objects.filter(
			token = self,
			unlockable = u,
		).exists()
	def has_unlocked(self, u : Optional[Unlockable]) -> bool:
		if u is None:
			return self.omniscient
		if hasattr(u, 'ustatus'):
			return u.ustatus == 0 or u.ustatus == 1 # type: ignore
		return Attempt.objects.filter(
			token = self,
			unlockable = u,
			status__gte = 0
		).exists()
	def has_solved(self, u : Unlockable) -> bool:
		if u is None:
			return self.omniscient
		if hasattr(u, 'ustatus'):
			return u.ustatus == 1 # type: ignore
		return Attempt.objects.filter(
			token = self,
			unlockable = u,
			status = 1
		).exists()

def get_viewable(queryset : models.QuerySet, token : Token):
	courage = token.get_courage()
	queryset = queryset.select_related(
			'puzzle',
			'round',
			'unlock_needs')
	queryset = queryset.annotate(
			ustatus = Max('attempt__status',
				filter = Q(attempt__token = token)
				),
			rstatus = Max('unlock_needs__attempt__status',
				filter = Q(unlock_needs__attempt__token = token)
				),
			)
	queryset = queryset.exclude(Q(force_visibility=False),
			Q(ustatus__isnull=True) | Q(ustatus__lt=0)
			)
	queryset = queryset.exclude(Q(force_visibility__isnull=True),
			Q(ustatus__isnull=True),
			Q(unlock_date__gt = timezone.now())
			| Q(unlock_courage_threshold__gt = courage)
			| (Q(unlock_needs__isnull=False)
				& (Q(rstatus__isnull=True) |
					Q(rstatus__lt=1))))
	return queryset

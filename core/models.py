from django.db import models
from django.db.models import Q, Max
from django.urls import reverse_lazy
from django.utils import timezone

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
	description = models.TextField(
			help_text = "The text to display for this hunt",
			blank = True)
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

class Unlockable(models.Model):
	hunt = models.ForeignKey(Hunt,
			help_text = "The hunt this unlockable belongs to",
			on_delete = models.CASCADE,
			)
	parent = models.ForeignKey('Unlockable',
			help_text = "Specifies a parent unlockable",
			null = True, blank = True,
			on_delete = models.SET_NULL,
			related_name = 'children',
			)
	name = models.CharField(max_length=80,
			help_text = "The name for this unlockable (e.g. place on map)",
			)
	slug = models.SlugField(
			help_text = "The slug for the unlockable",
			unique = True,
			)
	icon = models.CharField(max_length = 5,
			help_text = "Emoji for this unlockable",
			blank = True,
			)

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
	@property
	def is_puzzle(self):
		return hasattr(self, 'puzzle')
	@property
	def is_round(self):
		return hasattr(self, 'round')
	@property
	def prereqs_summary(self):
		s = f'{self.unlock_courage_threshold}💜'
		if self.unlock_date:
			s += '@' + self.unlock_date.isoformat()
		if self.unlock_needs:
			s += '/' + self.unlock_needs.slug
		return s
	@property
	def parent_abbrv(self):
		if self.is_round:
			return f'Vol {self.hunt.volume_number}'
		elif self.parent is not None:
			if self.parent.is_round:
				return f'Ch {self.parent.round.chapter_number}'
			return str(self.parent)
		else:
			return None

	def __str__(self):
		return self.slug
	def get_absolute_url(self):
		return reverse_lazy('unlockable-detail', args=(self.slug,))

class Puzzle(models.Model):
	unlockable = models.OneToOneField(Unlockable,
			help_text = "Associated unlockable for this puzzle",
			null = True, blank = True,
			on_delete = models.SET_NULL)
	name = models.CharField(max_length = 80)
	slug = models.SlugField(
			help_text = "The slug for the puzzle",
			unique = True,
			)
	display_answer = models.CharField(max_length = 128,
			help_text = "Display answer for the puzzle")
	is_meta = models.BooleanField(
			help_text = "Whether this is a metapuzzle",
			default = False)
	content = models.TextField(
			help_text = "Markdown for the puzzle content",
			blank = True,
			)
	pre_solve_story = models.TextField(
			help_text = "Markdown for the pre-solve story",
			blank = True,
			)
	puzzle_head = models.TextField(
			help_text = "Extra HTML to include in <head>",
			blank = True,
			)
	def get_absolute_url(self):
		return reverse_lazy('puzzle-detail', args=(self.slug,))
	def get_solution_url(self):
		return reverse_lazy('solution-detail', args=(self.slug,))
	def get_parent_url(self):
		return self.unlockable.parent.round.get_absolute_url()
	def __str__(self):
		return self.name
	@property
	def target_hashes(self):
		return [sa.hash for sa in self.salted_answers.all()] # type: ignore

class Solution(models.Model):
	puzzle = models.OneToOneField(Puzzle,
			help_text = "The puzzle this is a solution for",
			on_delete = models.CASCADE
			)
	post_solve_story = models.TextField(
			help_text = "Markdown for the post-solve story",
			blank = True,
			)
	solution_text = models.TextField(
			help_text = "Markdown for the puzzle solution",
			blank = True,
			)
	author_notes = models.TextField(
			help_text = "Markdown for the author's notes",
			blank = True,
			)
	post_solve_image_path = models.CharField(max_length = 240,
			help_text = "Static path to the post-solve image",
			blank = True
			)
	post_solve_image_alt = models.TextField(
			help_text = "Static path to the post-solve image",
			blank = True
			)
	def get_solution_url(self):
		return reverse_lazy('solution-detail', args=(self.puzzle.slug,))

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
			help_text = "For partial answers, the nudge to provide solvers.",
			blank = True)
	@property
	def is_final(self):
		return self.message == ''
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

class Round(models.Model):
	unlockable = models.OneToOneField(Unlockable,
			help_text = "Associated unlockable for this round",
			null = True, blank = True,
			on_delete = models.SET_NULL)
	name = models.CharField(max_length = 80)
	chapter_number = models.CharField(max_length = 80,
			help_text = "Chapter number for flavor",
			unique = True)
	slug = models.SlugField(
			help_text = "The slug for the round",
			unique = True,
			)
	thumbnail_path = models.CharField(max_length = 80,
			help_text = "Static argument for thumbnail image",
			blank = True)
	summary_text = models.TextField(
			help_text = "Any text to show in the round page",
			blank = True)
	intro_story_text = models.TextField(
			help_text = "Markdown for the pre-entry story",
			blank = True)
	round_text = models.TextField(
			help_text = "Markdown for content in the round page",
			blank = True)
	def get_absolute_url(self):
		return reverse_lazy('unlockable-list', args=(self.chapter_number,))
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
	name = models.CharField(max_length = 128,
			help_text = "Who are you?")
	reduced_name = models.CharField(max_length = 128,
			help_text = "Name with only [a-z0-9] characters.")
	hints_obtained = models.ManyToManyField(Hint,
			help_text = "Hints purchased by this token")
	attempts = models.ManyToManyField(Unlockable, through=Attempt,
			help_text = "Attempts attached to this token")
	passphrase = models.CharField(max_length = 256,
			verbose_name = "Magic word",
			help_text = "Magic word needed for a different account")
	reduced_passphrase = models.CharField(max_length = 256,
			help_text = "Passphrasew ith only [a-z0-9] characters")
	class Meta:
		unique_together = ('reduced_name', 'reduced_passphrase')

	@staticmethod
	def reduce(s : str):
		return re.sub(r'\W+', '', s.lower())
	def save(self, *args, **kwargs):
		self.reduced_name = self.reduce(self.name)
		self.reduced_passphrase = self.reduce(self.name)
		super().save(*args, **kwargs)
	

	def __str__(self):
		return self.name
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

	def can_view(self, u : Unlockable) -> bool:
		if u.force_visibility is True:
			return True
		elif u.force_visibility is False:
			return False
		else:
			return self.can_unlock(u)
	def has_found(self, u : Unlockable) -> bool:
		if hasattr(u, 'ustatus'):
			return u.ustatus is not None # type: ignore
		return Attempt.objects.filter(
			token = self,
			unlockable = u,
		).exists()
	def has_unlocked(self, u : Unlockable) -> bool:
		if hasattr(u, 'ustatus'):
			return u.ustatus == 0 or u.ustatus == 1 # type: ignore
		return Attempt.objects.filter(
			token = self,
			unlockable = u,
			status__gte = 0
		).exists()
	def has_solved(self, u : Unlockable) -> bool:
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

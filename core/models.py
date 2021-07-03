from django.db import models
from django.db.models import Q, OuterRef, Exists
from django.urls import reverse_lazy
from django.utils import timezone
import uuid
import random
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
			"use false if you're just testing")
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
			)
	icon = models.CharField(max_length = 5,
			help_text = "Emoji for this unlockable",
			blank = True,
			)

	unlock_courage_threshold = models.IntegerField(
			default = 0,
			help_text = "Amount of courage needed to unlock"
			)
	unlock_date = models.DateTimeField(
			null = True,
			blank = True,
			help_text = "When the unlockable can be unlocked"
			)
	unlock_needs = models.ForeignKey('Unlockable',
			help_text = "If this is nonempty, "
				"then unlock only when the target is done",
			null = True, blank = True,
			on_delete = models.SET_NULL,
			related_name = 'blocked_on',
			)
	force_visibility = models.BooleanField(
			null = True,
			blank = True,
			help_text = "Always show or hide"
			)
	courage_bounty = models.IntegerField(
			help_text = "Amount of courage obtained by solving",
			default = 25,
			)
	@property
	def is_puzzle(self):
		return hasattr(self, 'puzzle')
	@property
	def is_round(self):
		return hasattr(self, 'round')
	def __str__(self):
		if self.is_puzzle:
			return '[P] ' + self.name
		elif self.is_round:
			return '[R] ' + self.name
		else:
			return self.name
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
			)
	is_meta = models.BooleanField(
			help_text = "Whether this is a metapuzzle",
			default = False)
	content = models.TextField(
			help_text = "Markdown for the puzzle content",
			blank = True,
			)
	solution = models.TextField(
			help_text = "Markdown for the puzzle solution",
			blank = True,
			)
	author_notes = models.TextField(
			help_text = "Markdown for the author's notes",
			blank = True,
			)
	post_solve_story = models.TextField(
			help_text = "Markdown for the post-solve story",
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
	def __str__(self):
		return self.name
	@property
	def target_hashes(self):
		return [sa.hash for sa in self.salted_answers.all()] # type: ignore

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
		return sha('MOSP_LIGHT_NOVEL_' + self.normalized_answer + str(self.salt))
	@property
	def normalized_answer(self) -> str:
		return normalize(self.display_answer)
	def equals(self, other):
		return self.normalized_answer == normalize(self.display_answer)
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
			)
	content = models.TextField(
			help_text = "Any text to show in the round page",
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

class Solve(models.Model):
	token = models.ForeignKey('Token',
			help_text = "The token this solve attempt is for",
			on_delete = models.CASCADE)
	unlockable = models.ForeignKey(Unlockable,
			on_delete = models.CASCADE)
	answer_guesses = models.TextField(
			help_text = "Newline separated list of answer guesses"
			)
	unlocked_on = models.DateTimeField(
			help_text = "When this puzzle or round was unlocked",
			auto_now_add = True,
			)
	solved_on = models.DateTimeField(
			help_text = "When this puzzle or round was solved",
			null = True
			)
	class Meta:
		unique_together = ('token', 'unlockable')

class Token(models.Model):
	uuid = models.UUIDField(
			primary_key = True,
			default = uuid.uuid4,
			editable = False)
	name = models.CharField(max_length = 128,
			help_text = "Who are you?")
	hints_obtained = models.ManyToManyField(Hint,
			help_text = "Hints purchased by this token")
	def __str__(self):
		return self.name
	@property
	def firstname(self):
		if not ' ' in self.name:
			return self.name
		return self.name[:self.name.index(' ')]
	def get_courage(self):
		return Solve.objects.filter(token = self, solved_on__isnull = False)\
				.aggregate(courage = models.Sum('unlockable__courage_bounty'))['courage']\
				or 0
	
	def can_unlock(self, u : Unlockable):
		if u.unlock_date is not None:
			if u.unlock_date > timezone.now():
				return False
		if u.unlock_needs is not None:
			if not Solve.objects.filter(
				token = self,
				unlockable = u.unlock_needs,
			).exists():
				return False
		return self.get_courage() >= u.unlock_courage_threshold

def get_unlockable(queryset, token):
	courage = token.get_courage()
	queryset = queryset.filter(unlock_courage_threshold__lte=courage)
	queryset = queryset.exclude(unlock_date__isnull = True,
			unlock_date__gt = timezone.now())
	queryset = queryset.exclude(Q(unlock_needs__isnull = False),
			~Exists(
				Solve.objects.filter(
					token=token,
					unlockable=OuterRef('unlock_needs'),
					solved_on__isnull = True,
					)
				)
			)
	return queryset
def get_viewable(queryset, token):
	unlockable = get_unlockable(queryset, token)
	unlockable = unlockable.exclude(Q(force_visibility=False),
			~Exists(
				Solve.objects.filter(
					token=token,
					unlockable=OuterRef('pk')
					)
				)
			)
	return unlockable.union(queryset.filter(force_visibility=True))

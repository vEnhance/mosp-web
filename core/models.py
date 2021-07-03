from django.db import models
from django.urls import reverse_lazy
import uuid
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
		return reverse_lazy('round-list', args=(self.volume_number,))

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

	unlock_threshold = models.IntegerField(
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

class Puzzle(models.Model):
	unlockable = models.OneToOneField(Unlockable,
			help_text = "Associated unlockable for this puzzle",
			null = True, blank = True,
			on_delete = models.SET_NULL)
	name = models.CharField(max_length = 80)
	slug = models.SlugField(
			help_text = "The slug for the puzzle",
			)
	answer = models.CharField(max_length = 80,
			help_text = "Display answer to the puzzle",
			)
	answer_salt = models.SmallIntegerField(
			help_text = "A random number from 0000 to 9999",
			default = 0
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

class Round(models.Model):
	unlockable = models.OneToOneField(Unlockable,
			help_text = "Associated unlockable for this round",
			null = True, blank = True,
			on_delete = models.SET_NULL)
	name = models.CharField(max_length = 80)
	chapter_number = models.CharField(max_length = 80,
			help_text = "Chapter number/etc. for flavor")
	slug = models.SlugField(
			help_text = "The slug for the round",
			)
	content = models.TextField(
			help_text = "Any text to show in the round page",
			blank = True)
	def get_absolute_url(self):
		return reverse_lazy('puzzle-list', args=(self.slug,))
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
		return str(self.uuid)

class Solve(models.Model):
	token = models.ForeignKey(Token,
			help_text = "The token this solve attempt is for",
			on_delete = models.CASCADE)
	puzzle = models.ForeignKey(Puzzle,
			on_delete = models.CASCADE)
	answer_guesses = models.TextField(
			help_text = "Newline separated list of answer guesses"
			)
	unlocked_on = models.DateTimeField(
			help_text = "When this puzzle was unlocked",
			auto_now_add = True,
			)
	solved_on = models.DateTimeField(
			help_text = "When this puzzle was solved",
			null = True
			)

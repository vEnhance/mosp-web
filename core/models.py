from django.db import models
import uuid
# Create your models here.

class Hunt(models.Model):
	number = models.SmallIntegerField(
			help_text = "The number of the hunt",
			unique = True)
	name = models.CharField(max_length = 80,
			help_text = "The name of this hunt.")
	authors = models.CharField(max_length = 255,
			help_text = "The credits for this hunt.")
	description = models.TextField(
			help_text = "The text to display for this hunt.")
	start_date = models.DateTimeField(
			help_text = "When the hunt can be started.")
	visible = models.BooleanField(
			help_text = "Whether the hunt is visible to people; "
			"use false if you're just testing.")
	def __str__(self):
		return self.name
	def get_absolute_url(self):
		return '/'

class Puzzle(models.Model):
	title = models.CharField(max_length = 80)
	hunt = models.ForeignKey(Hunt,
			help_text = "The hunt that this puzzle belongs to",
			on_delete = models.CASCADE,
			)
	parent = models.ForeignKey('Puzzle',
			help_text = "If this is nonempty, specifies a parent. " \
					"If null, then this puzzle is really a round.",
			null = True,
			on_delete = models.SET_NULL,
			related_name = 'children',
			)
	is_meta = models.BooleanField(
			help_text = "Whether this is a metapuzzle.")
	@property
	def is_round(self) -> bool:
		return self.parent == None

	slug = models.SlugField(
			help_text = "The slug for the puzzle or round.",
			)
	answer = models.CharField(max_length = 80,
			help_text = "Display answer to the puzzle " \
					"Should be blank for rounds",
			blank = True,
			)
	answer_salt = models.SmallIntegerField(
			help_text = "A random number from 0000 to 9999",
			default = 0
			)

	icon = models.CharField(max_length = 5,
			help_text = "The icon associated to this puzzle",
			blank = True,
			)
	place = models.CharField(max_length = 80,
			help_text = "The location associated to this puzzle",
			blank = True,
			)
	place_slug = models.SlugField(
			help_text = "Slug for the location in the map"
			)

	unlock_threshold = models.IntegerField(
			default = 0,
			help_text = "Amount of courage needed to unlock."
			)
	unlock_date = models.DateTimeField(
			null = True,
			help_text = "When the puzzle can be unlocked."
			)
	unlock_needs = models.ForeignKey('Puzzle',
			help_text = "If this is nonempty, "
				"then unlock only when the target puzzle is done.",
			null = True,
			on_delete = models.SET_NULL,
			related_name = 'blocked_on',
			)
	force_visibility = models.BooleanField(
			null = True,
			help_text = "If True, always show; if False, always hide."
			)

	courage_bounty = models.IntegerField(
			help_text = "Amount of courage obtained by solving.",
			default = 25,
			)
	content = models.TextField(
			help_text = "Markdown for the puzzle content.",
			blank = True,
			)
	solution = models.TextField(
			help_text = "Markdown for the puzzle solution.",
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
			)

	def __str__(self):
		return self.title
	def get_absolute_url(self):
		raise NotImplementedError("To be written")

class Token(models.Model):
	uuid = models.UUIDField(
			primary_key = True,
			default = uuid.uuid4,
			editable = False)

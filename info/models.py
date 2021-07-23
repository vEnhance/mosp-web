from django.db import models
from django.urls import reverse_lazy
from markdownx.models import MarkdownxField

# Create your models here.

class Page(models.Model):
	title = models.CharField(max_length = 255,
			help_text = "Title of the page")
	content = MarkdownxField(
			help_text = "Markdown content for the page")
	slug = models.SlugField(unique = True,
			help_text = "The slug for the page")
	published = models.BooleanField(
			help_text = "Whether this page is published.",
			default = True)
	listed = models.BooleanField(
			help_text = "Whether this page is listed.",
			default = True)
	def __str__(self):
		return self.title
	def get_absolute_url(self):
		return reverse_lazy('page-detail', args=(self.slug,))
	def get_editor_url(self):
		return reverse_lazy('page-update', args=(self.slug,))

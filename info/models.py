from django.db import models

# Create your models here.

class Page(models.Model):
	title = models.CharField(max_length = 255,
			help_text = "Title of the page")
	content = models.TextField(
			help_text = "Markdown content for the page")
	slug = models.SlugField(unique = True,
			help_text = "The slug for the page")
	def __str__(self):
		return self.title

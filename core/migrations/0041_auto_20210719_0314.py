# Generated by Django 3.2.5 on 2021-07-19 03:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_token_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='round',
            name='show_chapter_number',
            field=models.BooleanField(default=True, help_text='Whether the chapter should be numbered on screen'),
        ),
        migrations.AlterField(
            model_name='round',
            name='chapter_number',
            field=models.CharField(help_text='Chapter identifier for the database', max_length=80, unique=True),
        ),
    ]
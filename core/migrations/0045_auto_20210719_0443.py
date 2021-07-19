# Generated by Django 3.2.5 on 2021-07-19 04:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0044_alter_unlockable_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='round',
            name='intro_story_text',
        ),
        migrations.AddField(
            model_name='unlockable',
            name='intro_story_text',
            field=models.TextField(blank=True, help_text='Markdown for the pre-entry story'),
        ),
        migrations.AddField(
            model_name='unlockable',
            name='on_solve_link_to',
            field=models.ForeignKey(blank=True, help_text='When solved, link to this instead', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='redirected_by', to='core.unlockable'),
        ),
    ]
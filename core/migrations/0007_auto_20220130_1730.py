# Generated by Django 3.2.11 on 2022-01-30 17:30

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_alter_puzzle_puzzle_head"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="hunt",
            name="allow_skip",
        ),
        migrations.AddField(
            model_name="hunt",
            name="end_date",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                help_text="Show solutions after this date",
            ),
            preserve_default=False,
        ),
    ]

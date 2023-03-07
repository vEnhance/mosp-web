# Generated by Django 3.2.5 on 2021-07-24 05:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_puzzle_status_progress"),
    ]

    operations = [
        migrations.AlterField(
            model_name="puzzle",
            name="status_progress",
            field=models.SmallIntegerField(
                choices=[
                    (-1, "Deferred"),
                    (0, "Initialized"),
                    (1, "Writing"),
                    (2, "Testsolving"),
                    (3, "Revising"),
                    (4, "Needs Soln"),
                    (5, "Polish"),
                    (6, "Finished"),
                    (7, "Published"),
                ],
                default=0,
                help_text="How far this puzzle is in the development process",
            ),
        ),
    ]

# Generated by Django 3.2.5 on 2021-07-24 06:48

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_alter_puzzle_status_progress"),
    ]

    operations = [
        migrations.CreateModel(
            name="TestSolveSession",
            fields=[
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "expires",
                    models.DateTimeField(
                        verbose_name="When the test solve session (and hence this link) expires"
                    ),
                ),
                (
                    "puzzle",
                    models.ForeignKey(
                        help_text="The puzzle this is a test solve session for",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.puzzle",
                    ),
                ),
            ],
        ),
    ]

# Generated by Django 3.2.12 on 2022-04-30 21:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0007_auto_20220130_1730"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="token",
            name="reduced_name",
        ),
        migrations.AlterField(
            model_name="token",
            name="name",
            field=models.CharField(
                blank=True, help_text="Who are you?", max_length=128
            ),
        ),
    ]

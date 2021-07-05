# Generated by Django 3.2.4 on 2021-07-05 04:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_alter_token_passphrase'),
    ]

    operations = [
        migrations.AddField(
            model_name='token',
            name='permission',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Normal user'), (20, 'Testsolver'), (40, 'Bestsolver'), (60, 'Editor'), (80, 'Admin'), (100, 'Evan Chen')], default=0, help_text='Whether this token has any elevated permissions'),
        ),
        migrations.AlterField(
            model_name='token',
            name='hints_obtained',
            field=models.ManyToManyField(blank=True, help_text='Hints purchased by this token', to='core.Hint'),
        ),
    ]

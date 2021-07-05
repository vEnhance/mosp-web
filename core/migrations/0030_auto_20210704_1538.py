# Generated by Django 3.2.4 on 2021-07-04 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_auto_20210704_0411'),
    ]

    operations = [
        migrations.AddField(
            model_name='hunt',
            name='thumbnail_path',
            field=models.CharField(blank=True, help_text='Static argument for thumbnail image', max_length=80),
        ),
        migrations.AddField(
            model_name='round',
            name='thumbnail_path',
            field=models.CharField(blank=True, help_text='Static argument for thumbnail image', max_length=80),
        ),
    ]
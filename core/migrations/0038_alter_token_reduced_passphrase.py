# Generated by Django 3.2.4 on 2021-07-05 04:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_auto_20210705_0436'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='reduced_passphrase',
            field=models.CharField(help_text='Passphrase with only [a-z0-9] characters', max_length=256),
        ),
    ]

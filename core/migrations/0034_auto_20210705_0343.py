# Generated by Django 3.2.4 on 2021-07-05 03:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_auto_20210705_0242'),
    ]

    operations = [
        migrations.AddField(
            model_name='token',
            name='passphrase',
            field=models.CharField(default='DARK BLUE', help_text='Magic word needed for a different account', max_length=256, verbose_name='Magic word'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='token',
            name='reduced_passphrase',
            field=models.CharField(default='darkblue', help_text='Passphrasew ith only [a-z0-9] characters', max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='token',
            name='reduced_name',
            field=models.CharField(help_text='Name with only [a-z0-9] characters.', max_length=128),
        ),
        migrations.AlterUniqueTogether(
            name='token',
            unique_together={('reduced_name', 'reduced_passphrase')},
        ),
        migrations.RemoveField(
            model_name='token',
            name='hashed_passphrase',
        ),
    ]

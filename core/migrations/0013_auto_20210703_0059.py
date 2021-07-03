# Generated by Django 3.2.4 on 2021-07-03 00:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20210703_0053'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='round',
            name='number',
        ),
        migrations.AddField(
            model_name='round',
            name='label_number',
            field=models.CharField(default='0', help_text='Chapter number/etc. for flavor', max_length=80),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='puzzle',
            name='unlockable',
            field=models.OneToOneField(help_text='Associated unlockable for this puzzle.', null=True, on_delete=django.db.models.deletion.CASCADE, to='core.unlockable'),
        ),
        migrations.AlterField(
            model_name='round',
            name='unlockable',
            field=models.OneToOneField(help_text='Associated unlockable for this round.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.unlockable'),
        ),
    ]

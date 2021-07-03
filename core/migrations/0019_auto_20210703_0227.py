# Generated by Django 3.2.4 on 2021-07-03 02:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_alter_solve_unlocked_on'),
    ]

    operations = [
        migrations.RenameField(
            model_name='unlockable',
            old_name='unlock_threshold',
            new_name='unlock_courage_threshold',
        ),
        migrations.RemoveField(
            model_name='solve',
            name='puzzle',
        ),
        migrations.AddField(
            model_name='solve',
            name='unlockable',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='core.unlockable'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='solve',
            name='solved_on',
            field=models.DateTimeField(help_text='When this puzzle or round was solved', null=True),
        ),
        migrations.AlterField(
            model_name='solve',
            name='unlocked_on',
            field=models.DateTimeField(auto_now_add=True, help_text='When this puzzle or round was unlocked'),
        ),
    ]
# Generated by Django 3.2.19 on 2023-06-19 12:02

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Voting_System', '0010_alter_candidate_candidate_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='voters',
            name='phone',
            field=models.CharField(default=django.utils.timezone.now, max_length=50),
            preserve_default=False,
        ),
    ]

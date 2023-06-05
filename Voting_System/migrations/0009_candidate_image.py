# Generated by Django 3.2.19 on 2023-06-03 21:25

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Voting_System', '0008_votes_portfolio'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='image',
            field=models.ImageField(default=django.utils.timezone.now, upload_to='images/'),
            preserve_default=False,
        ),
    ]

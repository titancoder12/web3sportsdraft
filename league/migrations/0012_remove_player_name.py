# Generated by Django 5.1.3 on 2025-03-07 20:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('league', '0011_auto_20250307_2008'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='name',
        ),
    ]

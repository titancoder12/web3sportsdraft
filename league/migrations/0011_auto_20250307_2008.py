# league/migrations/0009_migrate_name_data.py
from django.db import migrations

def migrate_name_to_first_last(apps, schema_editor):
    Player = apps.get_model('league', 'Player')
    for player in Player.objects.all():
        if player.name:  # Check if name exists
            names = player.name.split(' ', 1)  # Split on first space
            player.first_name = names[0]
            player.last_name = names[1] if len(names) > 1 else ''
            player.save()

def reverse_migrate_name(apps, schema_editor):
    Player = apps.get_model('league', 'Player')
    for player in Player.objects.all():
        player.name = f"{player.first_name} {player.last_name}".strip()
        player.save()

class Migration(migrations.Migration):
    dependencies = [
        ('league', '0010_player_first_name_player_last_name'),  # Previous migration
    ]

    operations = [
        migrations.RunPython(migrate_name_to_first_last, reverse_migrate_name),
    ]
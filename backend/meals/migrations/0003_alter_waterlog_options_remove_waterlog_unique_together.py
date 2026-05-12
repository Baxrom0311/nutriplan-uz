from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0002_alter_meal_meal_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='waterlog',
            options={'ordering': ['-date', '-created_at']},
        ),
        migrations.AlterUniqueTogether(
            name='waterlog',
            unique_together=set(),
        ),
    ]

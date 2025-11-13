# Generated manually for Task 3.3
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='useranswer',
            name='ai_explanation',
            field=models.TextField(blank=True, help_text='AI-generated explanation for incorrect answer', null=True),
        ),
    ]

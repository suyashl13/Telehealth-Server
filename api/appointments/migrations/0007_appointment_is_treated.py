# Generated by Django 3.1.7 on 2021-04-23 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0006_apttoken_is_assigned'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='is_treated',
            field=models.BooleanField(default=False),
        ),
    ]
# Generated by Django 3.1.7 on 2021-04-16 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treatment', '0002_auto_20210416_1027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medicine',
            name='intake_time_4',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
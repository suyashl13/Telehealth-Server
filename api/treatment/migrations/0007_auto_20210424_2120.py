# Generated by Django 3.1.7 on 2021-04-24 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treatment', '0006_auto_20210424_1546'),
    ]

    operations = [
        migrations.AlterField(
            model_name='treatment',
            name='precautions',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]

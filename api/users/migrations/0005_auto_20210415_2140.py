# Generated by Django 3.1.7 on 2021-04-15 16:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_doctordetail_city'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doctordetail',
            name='hospital_address',
        ),
        migrations.RemoveField(
            model_name='doctordetail',
            name='hospital_name',
        ),
        migrations.RemoveField(
            model_name='doctordetail',
            name='hospital_photos',
        ),
    ]

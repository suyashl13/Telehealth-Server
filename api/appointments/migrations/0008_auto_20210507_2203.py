# Generated by Django 3.1.7 on 2021-05-07 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0007_appointment_is_treated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apttoken',
            name='slot',
            field=models.CharField(choices=[('Morning', 'Morning'), ('Afternoon', 'Afternoon'), ('Evening', 'Evening')], default='', max_length=10),
        ),
    ]

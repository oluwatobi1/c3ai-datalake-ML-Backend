# Generated by Django 3.0.3 on 2020-11-01 22:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imageapp', '0003_image_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='prediction',
            field=models.CharField(blank=True, max_length=32),
        ),
    ]

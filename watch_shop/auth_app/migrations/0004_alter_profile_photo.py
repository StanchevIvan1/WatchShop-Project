# Generated by Django 4.1.3 on 2022-11-30 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0003_profile_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='photo',
            field=models.ImageField(default='blank_profile_image.jpeg', upload_to='images'),
        ),
    ]

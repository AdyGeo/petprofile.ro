# Generated by Django 3.2.5 on 2021-10-24 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('petprofile', '0006_auto_20211024_1957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='breed',
            name='breed_name',
            field=models.CharField(max_length=35),
        ),
    ]

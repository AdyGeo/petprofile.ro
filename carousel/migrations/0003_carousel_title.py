# Generated by Django 3.2.5 on 2021-10-02 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carousel', '0002_auto_20210927_2204'),
    ]

    operations = [
        migrations.AddField(
            model_name='carousel',
            name='title',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]

# Generated by Django 3.2.5 on 2021-09-27 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carousel', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='carousel',
            options={'verbose_name': 'Banner', 'verbose_name_plural': 'Banners'},
        ),
        migrations.AlterField(
            model_name='carousel',
            name='active',
            field=models.BooleanField(default=1),
            preserve_default=False,
        ),
    ]

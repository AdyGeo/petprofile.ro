# Generated by Django 3.2.5 on 2021-09-27 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Carousel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.URLField()),
                ('banner_img', models.ImageField(upload_to='banners', verbose_name='Foto')),
                ('active', models.BooleanField(null=True)),
                ('position', models.IntegerField()),
            ],
        ),
    ]

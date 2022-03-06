# Generated by Django 3.2.5 on 2021-10-02 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('petprofile', '0002_comments'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comments',
            options={'ordering': ('created',), 'verbose_name_plural': 'comments'},
        ),
        migrations.AlterModelOptions(
            name='species',
            options={'verbose_name_plural': 'species'},
        ),
        migrations.AddField(
            model_name='comments',
            name='comment',
            field=models.TextField(default=1, max_length=1000),
            preserve_default=False,
        ),
    ]
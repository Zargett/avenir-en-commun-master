# Generated by Django 3.2.5 on 2021-07-21 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20210716_1830'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='id',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='chapter',
            name='id',
            field=models.IntegerField(default=1),
        ),
    ]

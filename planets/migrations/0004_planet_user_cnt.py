# Generated by Django 3.1.2 on 2020-10-19 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planets', '0003_auto_20201014_0247'),
    ]

    operations = [
        migrations.AddField(
            model_name='planet',
            name='user_cnt',
            field=models.IntegerField(default=0),
        ),
    ]

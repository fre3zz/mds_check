# Generated by Django 3.2.6 on 2021-08-20 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mdscheck', '0004_mdsmodel_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mdsmodel',
            name='number',
            field=models.IntegerField(default=0),
        ),
    ]
# Generated by Django 3.2.6 on 2021-08-20 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mdscheck', '0005_alter_mdsmodel_number'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mdsmodel',
            options={'ordering': ['number']},
        ),
        migrations.AlterField(
            model_name='images',
            name='name',
            field=models.CharField(choices=[('1', 'CD13_vs_CD11b'), ('2', 'CD13_vs_CD16'), ('3', 'CD11b_vs_CD16')], default=None, max_length=1),
        ),
    ]

# Generated by Django 3.2.13 on 2022-05-14 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base_de_dados', '0014_alter_indicepluviometrico_mes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicepluviometrico',
            name='media_pluviometrica',
            field=models.FloatField(verbose_name='Média pluviométrica em mm'),
        ),
    ]

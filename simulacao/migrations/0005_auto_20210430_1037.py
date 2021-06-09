# Generated by Django 3.2 on 2021-04-30 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simulacao', '0004_alter_simulacao_n_pavimentos'),
    ]

    operations = [
        migrations.AddField(
            model_name='simulacao',
            name='n_apts',
            field=models.IntegerField(blank=True, null=True, verbose_name='Número de apartamentos'),
        ),
        migrations.AlterField(
            model_name='simulacao',
            name='n_pavimentos',
            field=models.IntegerField(default=1, verbose_name='Número de pavimentos'),
        ),
    ]

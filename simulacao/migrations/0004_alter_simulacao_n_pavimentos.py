# Generated by Django 3.2 on 2021-04-26 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simulacao', '0003_demandasdeagua_simulação única'),
    ]

    operations = [
        migrations.AlterField(
            model_name='simulacao',
            name='n_pavimentos',
            field=models.IntegerField(blank=True, null=True, verbose_name='Número de pavimentos'),
        ),
    ]

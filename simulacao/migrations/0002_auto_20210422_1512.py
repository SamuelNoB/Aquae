# Generated by Django 3.2 on 2021-04-22 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simulacao', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='simulacao',
            name='n_pavimentos',
            field=models.IntegerField(blank=True, null=True, verbose_name='Número de apartamentos'),
        ),
        migrations.AlterField(
            model_name='simulacao',
            name='tipo_residencia',
            field=models.IntegerField(choices=[(0, 'casa'), (1, 'apartamento')], verbose_name='Tipo da residencia'),
        ),
    ]

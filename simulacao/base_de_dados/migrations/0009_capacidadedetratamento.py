# Generated by Django 3.2 on 2021-10-06 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base_de_dados', '0008_alter_caixadagua_volume'),
    ]

    operations = [
        migrations.CreateModel(
            name='CapacidadeDeTratamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min', models.IntegerField(default=0, verbose_name='Mínimo')),
                ('max', models.IntegerField(default=3000, verbose_name='Máximo')),
                ('volume', models.IntegerField(default=500, verbose_name='Volume')),
                ('valor', models.FloatField(default=6631, verbose_name='Valor em dólares')),
            ],
            options={
                'verbose_name': 'Capacidade de Tratamento',
                'verbose_name_plural': 'Capacidades de Tratamento',
                'ordering': ['min'],
            },
        ),
    ]

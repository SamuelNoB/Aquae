# Generated by Django 3.2 on 2021-05-26 22:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base_de_dados', '0003_auto_20210502_1850'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bombadeagua',
            options={'ordering': ['potencia'], 'verbose_name': "Bomba d'água", 'verbose_name_plural': "Bombas d'água"},
        ),
        migrations.CreateModel(
            name='TarifaDeAgua',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min', models.IntegerField(default=0, verbose_name='Faixa de consumo mínima')),
                ('max', models.IntegerField(verbose_name='Faixa de consumo máxima')),
                ('tarifa', models.FloatField(default=0, verbose_name='tarifa')),
                ('cidade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tarifas', to='base_de_dados.cidade', verbose_name='Cidade pertencente')),
            ],
            options={
                'verbose_name': 'Tarifa de água',
                'verbose_name_plural': 'Tarifas de água',
            },
        ),
    ]
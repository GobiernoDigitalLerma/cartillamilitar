# Generated by Django 5.0.7 on 2024-08-05 06:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Formulario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('a_paterno', models.CharField(max_length=100)),
                ('a_materno', models.CharField(max_length=100)),
                ('nombre', models.CharField(max_length=100)),
                ('fecha_nacimiento', models.DateField()),
                ('nacio_en', models.CharField(max_length=100)),
                ('hijo_de', models.CharField(max_length=100)),
                ('y_de', models.CharField(blank=True, max_length=100, null=True)),
                ('estado_civil', models.CharField(max_length=100)),
                ('ocupacion', models.CharField(max_length=100)),
                ('sabe_leer_escribir', models.BooleanField(blank=True, null=True)),
                ('grado_maximo_estudios', models.CharField(max_length=100)),
                ('domicilio', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=100)),
                ('creado_a_las', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uapaterno', models.CharField(max_length=15)),
                ('uapmaterno', models.CharField(max_length=15)),
                ('unombre', models.CharField(max_length=30)),
                ('calle', models.CharField(max_length=50)),
                ('numero', models.PositiveIntegerField()),
                ('colonia', models.CharField(max_length=60)),
                ('cp', models.PositiveIntegerField()),
                ('localidad', models.CharField(max_length=20)),
                ('municipio', models.CharField(max_length=20)),
                ('estado', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=10, unique=True)),
                ('is_validated', models.BooleanField(default=False)),
                ('email', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Cartilla.email')),
            ],
        ),
    ]
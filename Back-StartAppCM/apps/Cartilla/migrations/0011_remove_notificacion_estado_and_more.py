# Generated by Django 5.0.7 on 2024-08-19 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Cartilla', '0010_rename_fecha_notificacion_fecha_envio_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notificacion',
            name='estado',
        ),
        migrations.AlterField(
            model_name='notificacion',
            name='fecha_envio',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='notificacion',
            name='message',
            field=models.TextField(),
        ),
    ]
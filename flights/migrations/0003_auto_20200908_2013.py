# Generated by Django 2.2 on 2020-09-08 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flights', '0002_auto_20200908_2002'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flight',
            name='distance',
        ),
        migrations.RemoveField(
            model_name='flight',
            name='number_of_changes',
        ),
        migrations.RemoveField(
            model_name='flight',
            name='provider',
        ),
        migrations.AddField(
            model_name='flight',
            name='seat_class',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
    ]

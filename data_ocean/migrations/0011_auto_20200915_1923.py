# Generated by Django 3.0.7 on 2020-09-15 19:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_ocean', '0010_auto_20200910_1001'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='endpoint',
            options={'ordering': ['id'], 'verbose_name': 'ендпойнт реєстру'},
        ),
        migrations.AlterModelOptions(
            name='register',
            options={'ordering': ['id'], 'verbose_name': 'реєстр'},
        ),
    ]

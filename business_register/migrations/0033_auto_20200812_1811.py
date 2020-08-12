# Generated by Django 3.0.7 on 2020-08-12 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business_register', '0032_auto_20200812_1720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='founder',
            name='edrpou',
            field=models.CharField(db_index=True, max_length=9, null=True, verbose_name='код ЄДРПОУ'),
        ),
        migrations.AlterField(
            model_name='historicalfounder',
            name='edrpou',
            field=models.CharField(db_index=True, max_length=9, null=True, verbose_name='код ЄДРПОУ'),
        ),
    ]

# Generated by Django 3.0.7 on 2021-05-07 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business_register', '0096_merge_20210507_1028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fop',
            name='contact_info',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='contacts'),
        ),
        migrations.AlterField(
            model_name='fop',
            name='vp_dates',
            field=models.CharField(blank=True, max_length=400, null=True),
        ),
        migrations.AlterField(
            model_name='historicalfop',
            name='contact_info',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='contacts'),
        ),
        migrations.AlterField(
            model_name='historicalfop',
            name='vp_dates',
            field=models.CharField(blank=True, max_length=400, null=True),
        ),
    ]

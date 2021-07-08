# Generated by Django 3.1.8 on 2021-07-06 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business_register', '0145_auto_20210706_1336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='income',
            name='paid_by_person',
            field=models.TextField(blank=True, default='', help_text='full name of the person that paid', verbose_name='paid by person'),
        ),
    ]

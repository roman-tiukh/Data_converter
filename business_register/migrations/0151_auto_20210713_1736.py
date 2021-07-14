# Generated by Django 3.1.12 on 2021-07-13 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business_register', '0150_auto_20210713_1544'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intangibleasset',
            name='cryptocurrency_type',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Bitcoin'), (2, 'Etherium'), (3, 'Ripple'), (4, 'NXT'), (5, 'Litecoin'), (6, 'Ravencoin'), (7, 'USDT'), (8, 'Zilliqa'), (9, 'Syntropy'), (10, 'Swissborg'), (11, 'EOS'), (12, 'Utrust'), (2, 'Etherium classic'), (14, 'XRP'), (15, 'BNB')], help_text='the name of the cryptocurrency', null=True),
        ),
    ]
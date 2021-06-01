# Generated by Django 3.1.8 on 2021-05-25 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business_register', '0105_auto_20210520_1056'),
    ]

    operations = [
        migrations.AddField(
            model_name='income',
            name='additional_info',
            field=models.TextField(blank=True, default='', help_text='additional info about the income', verbose_name='additional info'),
        ),
        migrations.AddField(
            model_name='income',
            name='from_info',
            field=models.CharField(blank=True, default='', help_text='info about citizenship or registration of the person or company that paid', max_length=55, verbose_name='info about citizenship or registration'),
        ),
        migrations.AlterField(
            model_name='company',
            name='source',
            field=models.CharField(blank=True, choices=[('ukr', 'The United State Register of Legal Entities, Individual Entrepreneurs and Public Organizations of Ukraine'), ('gb', 'Company House (UK companies` register)'), ('antac', 'ANTAC'), ('decl', 'Declarations')], db_index=True, default=None, help_text='Source', max_length=5, null=True, verbose_name='source'),
        ),
        migrations.AlterField(
            model_name='historicalcompany',
            name='source',
            field=models.CharField(blank=True, choices=[('ukr', 'The United State Register of Legal Entities, Individual Entrepreneurs and Public Organizations of Ukraine'), ('gb', 'Company House (UK companies` register)'), ('antac', 'ANTAC'), ('decl', 'Declarations')], db_index=True, default=None, help_text='Source', max_length=5, null=True, verbose_name='source'),
        ),
        migrations.AlterField(
            model_name='income',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Salary'), (2, 'Interest'), (3, 'Dividends'), (4, 'From sale of property'), (5, 'From sale of securities or corporate rights'), (6, 'Business'), (7, 'Gift in cash'), (8, 'Gift'), (9, 'Fees and other payments'), (10, 'Other'), (11, 'Income from renting property'), (12, 'Pension'), (13, 'Insurance payments'), (14, 'Sale of securities and corporate rights'), (15, 'Prize'), (16, 'Charity'), (17, 'Sale of property'), (18, 'Legacy'), (19, 'Salary from part-time job'), (20, 'Sale of luxuries'), (21, 'Self-employment')], help_text='type of income', verbose_name='type'),
        ),
    ]

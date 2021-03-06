# Generated by Django 3.1.12 on 2021-06-29 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business_register', '0129_personsanction_year_of_birth'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='luxuryitemright',
            name='country_of_citizenship',
        ),
        migrations.RemoveField(
            model_name='propertyright',
            name='country_of_citizenship',
        ),
        migrations.RemoveField(
            model_name='securitiesright',
            name='country_of_citizenship',
        ),
        migrations.RemoveField(
            model_name='vehicleright',
            name='country_of_citizenship',
        ),
        migrations.AddField(
            model_name='luxuryitemright',
            name='company_name',
            field=models.CharField(blank=True, help_text='name of the company that owns the right', max_length=200, verbose_name='company name'),
        ),
        migrations.AddField(
            model_name='luxuryitemright',
            name='owner_type',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Declarant'), (2, 'Family member'), (3, 'Ukraine citizen'), (4, 'Foreign citizen'), (5, 'Legal entity registered in Ukraine'), (6, 'Legal entity registered abroad')], help_text='type of the owner', null=True, verbose_name='owner type'),
        ),
        migrations.AddField(
            model_name='propertyright',
            name='company_name',
            field=models.CharField(blank=True, help_text='name of the company that owns the right', max_length=200, verbose_name='company name'),
        ),
        migrations.AddField(
            model_name='propertyright',
            name='owner_type',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Declarant'), (2, 'Family member'), (3, 'Ukraine citizen'), (4, 'Foreign citizen'), (5, 'Legal entity registered in Ukraine'), (6, 'Legal entity registered abroad')], help_text='type of the owner', null=True, verbose_name='owner type'),
        ),
        migrations.AddField(
            model_name='securitiesright',
            name='company_name',
            field=models.CharField(blank=True, help_text='name of the company that owns the right', max_length=200, verbose_name='company name'),
        ),
        migrations.AddField(
            model_name='securitiesright',
            name='owner_type',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Declarant'), (2, 'Family member'), (3, 'Ukraine citizen'), (4, 'Foreign citizen'), (5, 'Legal entity registered in Ukraine'), (6, 'Legal entity registered abroad')], help_text='type of the owner', null=True, verbose_name='owner type'),
        ),
        migrations.AddField(
            model_name='vehicleright',
            name='company_name',
            field=models.CharField(blank=True, help_text='name of the company that owns the right', max_length=200, verbose_name='company name'),
        ),
        migrations.AddField(
            model_name='vehicleright',
            name='owner_type',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Declarant'), (2, 'Family member'), (3, 'Ukraine citizen'), (4, 'Foreign citizen'), (5, 'Legal entity registered in Ukraine'), (6, 'Legal entity registered abroad')], help_text='type of the owner', null=True, verbose_name='owner type'),
        ),
    ]

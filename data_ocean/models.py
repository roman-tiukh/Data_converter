from django.db import models, connection
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class DataOceanModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    @property
    def is_deleted(self):
        return bool(self.deleted_at)

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at', 'updated_at'])

    @classmethod
    def truncate(cls):
        with connection.cursor() as c:
            c.execute('TRUNCATE TABLE "{0}"'.format(cls._meta.db_table))

    @classmethod
    def truncate_cascade(cls):
        with connection.cursor() as c:
            c.execute('TRUNCATE TABLE "{0}" CASCADE'.format(cls._meta.db_table))

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ['id']


class Status(DataOceanModel):
    name = models.CharField('назва', max_length=100, unique=True)

    class Meta:
        verbose_name = 'статус'


class Authority(DataOceanModel):
    name = models.CharField('назва', max_length=500, unique=True)
    code = models.CharField('код ЄДРПОУ', max_length=10, unique=True, null=True)

    class Meta:
        verbose_name = 'орган реєстрації'


class TaxpayerType(DataOceanModel):
    name = models.CharField('назва', max_length=200, unique=True)

    class Meta:
        verbose_name = 'тип платника податків'


class Register(DataOceanModel):
    RELEVANT = 'relevant'
    OUTDATED = 'outdated'
    NOT_SUPPORTED = 'not supported'
    STATUSES = [
        (RELEVANT, _('Relevant')),
        (OUTDATED, _('Outdated')),
        (NOT_SUPPORTED, _('Not supported')),
    ]
    name = models.CharField('назва', max_length=500, unique=True)
    name_eng = models.CharField('назва англійською', max_length=500, unique=True, null=True)
    source_name = models.CharField('назва джерела даних', max_length=300)
    source_register_id = models.CharField('ID реєстру у джерелі даних', max_length=36, null=True)
    source_url_address = models.URLField(max_length=500)
    source_api_address = models.URLField(max_length=500, null=True)
    api_list = models.CharField('ендпоінт списку', max_length=30, unique=True, null=True, blank=True)
    api_detail = models.CharField("ендпоінт об'єкта", max_length=30, unique=True, null=True, blank=True)
    total_records = models.PositiveIntegerField('кількість записів', default=1, blank=True)
    status = models.CharField('статус', max_length=15, choices=STATUSES, default=RELEVANT,
                              blank=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'реєстр'


class RegistryUpdaterModel(models.Model):
    registry_name = models.CharField(max_length=20, db_index=True)
    download_start = models.DateTimeField(auto_now_add=True)
    download_finish = models.DateTimeField(null=True, blank=True)
    download_status = models.BooleanField(blank=True, default=False)
    download_message = models.CharField(max_length=255, null=True, blank=True)
    download_file_name = models.CharField(max_length=255, null=True, blank=True)
    download_file_length = models.PositiveIntegerField(blank=True, default=0)

    unzip_file_name = models.CharField(max_length=255, null=True, blank=True)
    unzip_file_arch_length = models.PositiveIntegerField(blank=True, default=0)
    unzip_file_real_length = models.PositiveIntegerField(blank=True, default=0)
    unzip_status = models.BooleanField(blank=True, default=False)
    unzip_message = models.CharField(max_length=255, null=True, blank=True)

    update_start = models.DateTimeField(null=True, blank=True)
    update_finish = models.DateTimeField(null=True, blank=True)
    update_status = models.BooleanField(blank=True, default=False)
    update_message = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.registry_name

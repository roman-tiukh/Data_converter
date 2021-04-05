from django.db import models, connection
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class DataOceanManager(models.Manager):
    # exclude soft-deleted objects from queryset
    def get_queryset(self):
        return super().get_queryset().exclude(deleted_at__isnull=False)


class DataOceanModel(models.Model):
    name = "No name field in model!"

    created_at = models.DateTimeField(auto_now_add=True,
                                      help_text='When the object was created. In YYYY-MM-DDTHH:mm:ss.SSSSSSZ format.')
    updated_at = models.DateTimeField(
        auto_now=True, null=True, blank=True,
        help_text='When the object was update. In YYYY-MM-DDTHH:mm:ss.SSSSSSZ format.'
    )
    deleted_at = models.DateTimeField(null=True, blank=True, default=None, editable=False, db_index=True)

    objects = DataOceanManager()
    include_deleted_objects = models.Manager()

    @property
    def is_deleted(self):
        return bool(self.deleted_at)

    def soft_delete(self):
        if not self.deleted_at:
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
        return self.name or ''

    class Meta:
        abstract = True
        ordering = ['id']


class Status(DataOceanModel):
    name = models.CharField('name', max_length=100, unique=True)

    class Meta:
        verbose_name = _('status')


class Authority(DataOceanModel):
    name = models.CharField('name', max_length=500, unique=True)
    code = models.CharField('number', max_length=10, unique=True, null=True)

    class Meta:
        verbose_name = _('registration authority')


class TaxpayerType(DataOceanModel):
    name = models.CharField('name', max_length=200, unique=True)

    class Meta:
        verbose_name = _('taxpayer type')


class Register(DataOceanModel):
    RELEVANT = 'relevant'
    OUTDATED = 'outdated'
    NOT_SUPPORTED = 'not supported'
    STATUSES = [
        (RELEVANT, _('Up-to-date')),
        (OUTDATED, _('Outdated')),
        (NOT_SUPPORTED, _('Not supported')),
    ]
    name = models.CharField(_('name'), max_length=500, unique=True)
    name_eng = models.CharField('name eng', max_length=500, unique=True, null=True)
    source_name = models.CharField(_('source'), max_length=300)
    source_register_id = models.CharField(_('source ID'), max_length=36, null=True)
    source_url_address = models.URLField(_('source url'), max_length=500)
    source_api_address = models.URLField(_('source API'), max_length=500, null=True)
    api_list = models.CharField(_('API list'), max_length=30, unique=True, null=True, blank=True)
    api_detail = models.CharField(_("API detail"), max_length=30, unique=True, null=True, blank=True)
    total_records = models.PositiveIntegerField(_('total records'), default=1, blank=True)
    status = models.CharField(_('status'), max_length=15, choices=STATUSES, default=RELEVANT,
                              blank=True)

    class Meta:
        ordering = ['id']
        verbose_name = _('dataset')
        verbose_name_plural = _('datasets')


class Report(DataOceanModel):
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
    update_message = models.CharField(max_length=300, null=True, blank=True)

    records_added = models.IntegerField(blank=True, default=0)
    records_changed = models.IntegerField(blank=True, default=0)
    records_deleted = models.IntegerField(blank=True, default=0)
    invalid_data = models.IntegerField(blank=True, default=0)

    @staticmethod
    def collect_last_day_reports():
        day_ago = timezone.now() - timezone.timedelta(hours=24)
        return list(Report.objects.filter(created_at__gt=day_ago))

    def __str__(self):
        return self.registry_name

    class Meta:
        ordering = ['id']
        verbose_name = _('data update report')
        verbose_name_plural = _('data update reports')

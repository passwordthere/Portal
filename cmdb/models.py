from django.db import models

from cmdb.model_utils import hv_id_prefix, vm_id_prefix


class Resource(models.Model):
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    remark = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True


class HV(Resource):
    id = models.CharField(primary_key=True, max_length=11, default=hv_id_prefix)
    name = models.CharField(db_index=True, max_length=100, unique=True)
    ip = models.GenericIPAddressField(help_text='内网地址', protocol='both', db_index=True, unique=True, blank=True, null=True)
    idrac = models.GenericIPAddressField(help_text='管理地址', protocol='both', db_index=True, unique=True, blank=True, null=True)
    os = models.CharField(max_length=255, blank=True, null=True)
    cpu_threads = models.PositiveSmallIntegerField(blank=True, null=True)
    mem_size = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    disk_size = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)

    class Meta:
        ordering = ['cpu_threads', 'mem_size', 'disk_size']


class VM(Resource):
    IS_TEMPLATE_CHOICES = [
        (1, '是'),
        (2, '不是'),
    ]
    id = models.CharField(primary_key=True, max_length=11, default=vm_id_prefix)
    name = models.CharField(db_index=True, max_length=100, unique=True)
    ip = models.GenericIPAddressField(help_text='内网地址', protocol='both', db_index=True, unique=True, blank=True, null=True)
    vip = models.GenericIPAddressField(help_text='虚拟地址', protocol='both', db_index=True, unique=True, blank=True, null=True)
    os = models.CharField(max_length=255, blank=True, null=True)
    cpu_threads = models.PositiveSmallIntegerField(blank=True, null=True)
    mem_size = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    disk_size = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)

    hv = models.ForeignKey(HV, models.PROTECT, blank=True, null=True)
    is_template = models.PositiveSmallIntegerField(help_text='是否是模板机', choices=IS_TEMPLATE_CHOICES, default=2)

    class Meta:
        ordering = ['cpu_threads', 'mem_size', 'disk_size']

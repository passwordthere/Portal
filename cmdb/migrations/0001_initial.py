# Generated by Django 4.0.3 on 2022-04-18 13:08

import cmdb.model_utils
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HV',
            fields=[
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True, null=True)),
                ('id', models.CharField(default=cmdb.model_utils.hv_id_prefix, max_length=11, primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=100, unique=True)),
                ('ip', models.GenericIPAddressField(blank=True, db_index=True, help_text='内网地址', null=True, unique=True)),
                ('idrac', models.GenericIPAddressField(blank=True, db_index=True, help_text='管理地址', null=True, unique=True)),
                ('os', models.CharField(blank=True, max_length=255, null=True)),
                ('cpu_threads', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('mem_size', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
                ('disk_size', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
            ],
            options={
                'ordering': ['cpu_threads', 'mem_size', 'disk_size'],
            },
        ),
        migrations.CreateModel(
            name='VM',
            fields=[
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('remark', models.TextField(blank=True, null=True)),
                ('id', models.CharField(default=cmdb.model_utils.vm_id_prefix, max_length=11, primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=100, unique=True)),
                ('ip', models.GenericIPAddressField(blank=True, db_index=True, help_text='内网地址', null=True, unique=True)),
                ('vip', models.GenericIPAddressField(blank=True, db_index=True, help_text='虚拟地址', null=True, unique=True)),
                ('os', models.CharField(blank=True, max_length=255, null=True)),
                ('cpu_threads', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('mem_size', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
                ('disk_size', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
                ('is_template', models.PositiveSmallIntegerField(choices=[(1, '是'), (2, '不是')], default=2, help_text='是否是模板机')),
                ('hv', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='cmdb.hv')),
            ],
            options={
                'ordering': ['cpu_threads', 'mem_size', 'disk_size'],
            },
        ),
    ]

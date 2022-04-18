import logging
import time

from MySQLdb._exceptions import IntegrityError

from agent.vcenter_operators import OperatorGirl
from pyVmomi import vim

from django.db import transaction
from rest_framework.response import Response
from rest_framework import views

from cmdb.models import HV, VM

VCENTER_IP = ['10.138.60.66', '10.10.250.237', '10.138.61.6']

logger = logging.getLogger(__name__)


def timer(func):
    def deco(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        print('总耗时 {_time_} 秒'.format(_time_=(round(end - start), 2)))
        return res

    return deco


class HVBornAPIView(views.APIView):
    @timer
    @transaction.atomic()
    def get(self, request):
        properties = ['name']
        for vcenter_ip in VCENTER_IP:
            hv_data = OperatorGirl(vcenter_ip).collect_properties(obj_type=vim.HostSystem, path_set=properties)
            # TODO Better to check ['summary.quickStats.uptime'] or what
            for hv in hv_data:
                try:
                    queryset = HV.objects.create(name=hv['name'])
                except KeyError:
                    logger.info(f'{hv.name}的某个字段unset')
                    continue
                except Exception:
                    logger.error(Exception)
                    return Response('HV初始化失败')
        return Response('HV初始化结束')


class VMBornAPIView(views.APIView):
    @timer
    @transaction.atomic()
    def get(self, request):
        properties = ['name', 'vm']
        for vcenter_ip in VCENTER_IP:
            try:
                create_list = []
                hv_data = OperatorGirl(vcenter_ip).collect_properties(obj_type=vim.HostSystem, path_set=properties)
                for hv in hv_data:
                    for vm in hv['vm']:
                        hv_id = HV.objects.filter(name=hv['name']).values_list('id', flat=True)
                        if vm.summary.config.template:
                            queryset = VM(name=vm.name, is_template=1, hv_id=hv_id)
                        else:
                            queryset = VM(name=vm.name, hv_id=hv_id)
                        create_list.append(queryset)
                VM.objects.bulk_create(create_list, ignore_conflicts=True)
            except Exception:
                logger.error(Exception)
        return Response('VM初始化结束')


class HVAliveAPIView(views.APIView):
    @timer
    @transaction.atomic()
    def get(self, request):
        properties = ['name', 'config.product.fullName', 'summary.hardware.numCpuThreads',
                      'summary.hardware.memorySize']
        obj = {}
        for vcenter_ip in VCENTER_IP:
            hv_data = OperatorGirl(vcenter_ip).collect_properties(obj_type=vim.HostSystem, path_set=properties)
            for hv in hv_data:
                obj['ip'] = hv['name']
                # obj['idrac'] = ''
                obj['os'] = ['config.product.fullName']
                obj['cpu_threads'] = hv['summary.hardware.numCpuThreads']
                obj['mem_size'] = hv['summary.hardware.memorySize'] / (1024 ** 3)
                # obj['disk_size'] = 0
                HV.objects.filter(name=hv['name']).update(ip=obj['ip'], idrac='', cpu_threads=obj['cpu_threads'],
                                                          mem_size=obj['mem_size'], disk_size=0)
        return Response('HV同步结束')


class VMAliveAPIView(views.APIView):
    @timer
    @transaction.atomic()
    def get(self, request):
        properties = ['name', 'summary.config.template', 'guest.net', 'config.guestFullName', 'config.hardware.numCPU',
                      'config.hardware.memoryMB', 'guest.disk', ]
        obj = {}
        for vcenter_ip in VCENTER_IP:
            update_list = []
            vm_data = OperatorGirl(vcenter_ip).collect_properties(obj_type=vim.VirtualMachine, path_set=properties)
            for vm in vm_data:
                if vm['guest.net']:
                    for ip_list in vm['guest.net']:
                        for ip in ip_list.ipAddress:
                            parts = ip.split('.')
                            if len(parts) == 4:
                                reset = parts[0] + '.' + parts[1] + '.' + parts[2] + '.0'
                                hv_queryset = HV.objects.all().values_list('name', flat=True)
                                if reset in hv_queryset:
                                    obj['ip'] = ip
                obj['disk_size'] = 0
                if vm['guest.disk']:
                    for d in vm['guest.disk']:
                        if d.diskPath == '/data':
                            obj['disk_size'] = d.capacity / (1024 ** 3)
                vm_instance = VM.objects.filter(name=vm['name']).first()
                vm_instance.ip = obj['ip']
                vm_instance.vip = ''
                vm_instance.os = vm['config.guestFullName']
                vm_instance.cpu_threads = vm['config.hardware.numCPU']
                vm_instance.mem_size = vm['config.hardware.memoryMB'] / 1024
                vm_instance.disk_size = obj['disk_size']
                update_list.append(vm_instance)
            VM.objects.bulk_update(update_list, ['ip', 'vip', 'os', 'cpu_num', 'mem_size', 'disk_size'])
        return Response('VM同步结束')

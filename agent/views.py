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
                    queryset = HV.objects.create(name=hv["name"])
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
        properties = ["name", "vm"]
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

from rest_framework import viewsets

from cmdb.models import HV, VM
from cmdb.serializers import HVSerializer, VMSerializer


class HVViewSet(viewsets.ModelViewSet):
    queryset = HV.objects.all()
    serializer_class = HVSerializer


class VMViewSet(viewsets.ModelViewSet):
    queryset = VM.objects.all()
    serializer_class = VMSerializer

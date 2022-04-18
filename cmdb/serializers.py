from rest_framework import serializers
from .models import HV, VM


class HVSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = HV
        fields = '__all__'


class VMSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = VM
        fields = '__all__'

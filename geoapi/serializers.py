from rest_framework import serializers
from .models import UploadedLayer

class UploadedLayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedLayer
        fields = '__all__'

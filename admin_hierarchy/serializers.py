from rest_framework import serializers
from django.conf import settings
from .models import DeviceToken


class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = ('id', 'token', 'platform', 'metadata', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_token(self, value):
        if not value or len(value) < 10:
            raise serializers.ValidationError('Invalid device token')
        return value

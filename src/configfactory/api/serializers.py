from django.urls import reverse
from rest_framework import serializers

from configfactory.models import Environment


class EnvironmentSerializer(serializers.Serializer):

    name = serializers.CharField()

    alias = serializers.CharField()

    fallback = serializers.SerializerMethodField()

    def get_fallback(self, environment: Environment):
        if environment.fallback_id:
            return environment.fallback.name
        return None

    def get_url(self, environment: Environment):
        request = self.context['request']
        return request.build_absolute_uri(
            reverse('api:settings', kwargs={
                'environment': environment.alias
            })
        )

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

from rest_framework import serializers

from apps.contribution.models import Repository, RepositoryLanguage


class RepositoryLanguagesSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = RepositoryLanguage
        fields = ('type', 'size', 'color')


class RepositorySerializer(serializers.ModelSerializer):
    languages = RepositoryLanguagesSerializer(many=True)

    class Meta:
        model = Repository
        fields = ('id', 'name', 'description', 'public_url', 'issues', 'updated_at', 'languages')

from rest_framework import serializers

from home.models import Banner, Nav


class BannerModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ('title', 'img', 'link')


class NavModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nav
        fields = ('title', 'is_site', 'link')

from rest_framework import serializers

from home.models import Banner, Nav


class BannerModelSerializer(serializers.ModelSerializer):
    """轮播图的序列化"""
    class Meta:
        model = Banner
        fields = ('title', 'img', 'link')


class NavModelSerializer(serializers.ModelSerializer):
    """导航栏的序列化"""
    class Meta:
        model = Nav
        fields = ('title', 'is_site', 'link')

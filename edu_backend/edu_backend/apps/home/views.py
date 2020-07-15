from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView

from edu_backend.settings.constants import BANNER_LENGTH, HEADER_NAV_LENGTH, FOOTER_NAV_LENGTH
from home.models import Banner, Nav
from home.serializers import BannerModelSerializer, NavModelSerializer


class BannerListAPIView(ListAPIView):
    queryset = Banner.objects.filter(is_show=True, is_delete=False).order_by('-orders')[:BANNER_LENGTH]
    serializer_class = BannerModelSerializer


class HeaderNavListAPIView(ListAPIView):
    queryset = Nav.objects.filter(is_show=True, is_delete=False, position=1).order_by('orders')[:HEADER_NAV_LENGTH]
    serializer_class = NavModelSerializer


class FooterNavListAPIView(ListAPIView):
    queryset = Nav.objects.filter(is_show=True, is_delete=False, position=2).order_by('orders')[:FOOTER_NAV_LENGTH]
    serializer_class = NavModelSerializer

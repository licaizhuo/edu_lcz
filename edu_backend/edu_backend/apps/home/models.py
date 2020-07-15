from django.db import models
from edu_backend.utils.BaseModels import BaseModel


# Create your models here.


class Banner(BaseModel):
    img = models.ImageField(upload_to="banner", verbose_name="轮播图片", blank=True)
    title = models.CharField(max_length=200, verbose_name="轮播图标题")
    link = models.CharField(max_length=300, verbose_name="轮播图链接")

    class Meta:
        db_table = "bz_banner"
        verbose_name = "轮播图"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Nav(BaseModel):
    POSITION_OPTION = (
        (1, "顶部导航"),
        (2, "底部导航"),
    )
    title = models.CharField(max_length=200, verbose_name="导航标题")
    link = models.CharField(max_length=300, verbose_name="导航链接")
    position = models.SmallIntegerField(choices=POSITION_OPTION, default=1, verbose_name="导航位置")
    is_site = models.BooleanField(default=False, verbose_name="是否是外部链接")

    class Meta:
        db_table = "bz_Nav"
        verbose_name = "导航栏"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

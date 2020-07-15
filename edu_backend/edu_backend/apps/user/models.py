from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class UserInfo(AbstractUser):
    phone = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    user_head = models.ImageField(upload_to="user", verbose_name="头像", blank=True, null=True, default="user/1.png")

    class Meta:
        db_table = "bz_user"
        verbose_name = "用户表"
        verbose_name_plural = verbose_name



# Generated by Django 4.2.4 on 2023-10-04 12:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import videomanager.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ExpandVideoModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("designator", models.CharField(max_length=80)),
                ("left", models.PositiveSmallIntegerField()),
                ("right", models.PositiveSmallIntegerField()),
                ("double", models.PositiveSmallIntegerField()),
                ("cl", models.PositiveSmallIntegerField()),
                ("left_s", models.FloatField()),
                ("right_s", models.FloatField()),
                ("double_s", models.FloatField()),
                ("cl_s", models.FloatField()),
                ("path", models.FloatField()),
                ("flag", models.PositiveSmallIntegerField()),
                ("flag_s", models.FloatField()),
                ("stnb", models.FloatField()),
                ("rqp", models.FloatField()),
                ("ioe", models.FloatField()),
                ("thrp", models.FloatField()),
                ("corr", models.FloatField()),
                ("ce", models.PositiveSmallIntegerField()),
                ("ce_s", models.FloatField()),
                ("op", models.PositiveSmallIntegerField()),
                ("isl", models.PositiveSmallIntegerField()),
                ("cell0", models.PositiveSmallIntegerField()),
                ("cell1", models.PositiveSmallIntegerField()),
                ("cell2", models.PositiveSmallIntegerField()),
                ("cell3", models.PositiveSmallIntegerField()),
                ("cell4", models.PositiveSmallIntegerField()),
                ("cell5", models.PositiveSmallIntegerField()),
                ("cell6", models.PositiveSmallIntegerField()),
                ("cell7", models.PositiveSmallIntegerField()),
                ("cell8", models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="VideoModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "file",
                    videomanager.fields.RestrictedFileField(upload_to="assets/videos"),
                ),
                (
                    "upload_time",
                    models.DateTimeField(auto_now_add=True, verbose_name="上传时间"),
                ),
                (
                    "state",
                    models.CharField(
                        choices=[("a", "已上传但未审核"), ("b", "审核为通过，被冻结"), ("c", "已通过审核")],
                        default="a",
                        max_length=1,
                    ),
                ),
                ("software", models.CharField(max_length=1)),
                (
                    "level",
                    models.CharField(
                        choices=[("b", "初级"), ("i", "中级"), ("e", "高级"), ("c", "自定义")],
                        max_length=1,
                    ),
                ),
                (
                    "mode",
                    models.CharField(
                        choices=[
                            ("00", "标准"),
                            ("01", "upk"),
                            ("04", "win7"),
                            ("05", "竞速无猜"),
                            ("06", "强无猜"),
                            ("07", "弱无猜"),
                            ("08", "准无猜"),
                            ("09", "强可猜"),
                            ("10", "弱可猜"),
                            ("11", "标准递归"),
                            ("12", "标准盲扫"),
                        ],
                        default="00",
                        max_length=2,
                    ),
                ),
                ("rtime", models.DecimalField(decimal_places=3, max_digits=6)),
                ("bv", models.PositiveSmallIntegerField()),
                ("bvs", models.FloatField()),
                (
                    "player",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "video",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="videomanager.expandvideomodel",
                    ),
                ),
            ],
        ),
    ]

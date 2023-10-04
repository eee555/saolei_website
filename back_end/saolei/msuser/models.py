from django.db import models
# from userprofile.models import UserProfile

# 扫雷用户
class UserMS(models.Model):
    # user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='profile')
    # realname = models.CharField(max_length=10, unique=False, blank=True, default='无名氏', null=False)
    # # 头像
    # avatar = models.ImageField(upload_to='avatar/%Y%m%d/', blank=True, null=True)
    # # 签名
    # bio = models.TextField(max_length=188, blank=True, null=True)

    # 标准、盲扫、竞速无猜、递归的记录
    b_time_std = models.DecimalField(max_digits=6, decimal_places=3, default=999.999)
    b_time_id_std = models.BigIntegerField(null=True)
    i_time_std = models.DecimalField(max_digits=6, decimal_places=3, default=999.999)
    i_time_id_std = models.BigIntegerField(null=True)
    e_time_std = models.DecimalField(max_digits=6, decimal_places=3, default=999.999)
    e_time_id_std = models.BigIntegerField(null=True)
    b_bvs_std = models.FloatField(default=0.0)
    b_bvs_id_std = models.BigIntegerField(null=True)
    i_bvs_std = models.FloatField(default=0.0)
    i_bvs_id_std = models.BigIntegerField(null=True)
    e_bvs_std = models.FloatField(default=0.0)
    e_bvs_id_std = models.BigIntegerField(null=True)
    b_stnb_std = models.FloatField(default=0.0)
    b_stnb_id_std = models.BigIntegerField(null=True)
    i_stnb_std = models.FloatField(default=0.0)
    i_stnb_id_std = models.BigIntegerField(null=True)
    e_stnb_std = models.FloatField(default=0.0)
    e_stnb_id_std = models.BigIntegerField(null=True)
    b_ioe_std = models.FloatField(default=0.0)
    b_ioe_id_std = models.BigIntegerField(null=True)
    i_ioe_std = models.FloatField(default=0.0)
    i_ioe_id_std = models.BigIntegerField(null=True)
    e_ioe_std = models.FloatField(default=0.0)
    e_ioe_id_std = models.BigIntegerField(null=True)
    b_path_std = models.FloatField(default=99999.9)
    b_path_id_std = models.BigIntegerField(null=True)
    i_path_std = models.FloatField(default=99999.9)
    i_path_id_std = models.BigIntegerField(null=True)
    e_path_std = models.FloatField(default=99999.9)
    e_path_id_std = models.BigIntegerField(null=True)

    b_time_nf = models.DecimalField(max_digits=6, decimal_places=3, default=999.999)
    b_time_id_nf = models.BigIntegerField(null=True)
    i_time_nf = models.DecimalField(max_digits=6, decimal_places=3, default=999.999)
    i_time_id_nf = models.BigIntegerField(null=True)
    e_time_nf = models.DecimalField(max_digits=6, decimal_places=3, default=999.999)
    e_time_id_nf = models.BigIntegerField(null=True)
    b_bvs_nf = models.FloatField(default=0.0)
    b_bvs_id_nf = models.BigIntegerField(null=True)
    i_bvs_nf = models.FloatField(default=0.0)
    i_bvs_id_nf = models.BigIntegerField(null=True)
    e_bvs_nf = models.FloatField(default=0.0)
    e_bvs_id_nf = models.BigIntegerField(null=True)
    b_stnb_nf = models.FloatField(default=0.0)
    b_stnb_id_nf = models.BigIntegerField(null=True)
    i_stnb_nf = models.FloatField(default=0.0)
    i_stnb_id_nf = models.BigIntegerField(null=True)
    e_stnb_nf = models.FloatField(default=0.0)
    e_stnb_id_nf = models.BigIntegerField(null=True)
    b_ioe_nf = models.FloatField(default=0.0)
    b_ioe_id_nf = models.BigIntegerField(null=True)
    i_ioe_nf = models.FloatField(default=0.0)
    i_ioe_id_nf = models.BigIntegerField(null=True)
    e_ioe_nf = models.FloatField(default=0.0)
    e_ioe_id_nf = models.BigIntegerField(null=True)
    b_path_nf = models.FloatField(default=99999.9)
    b_path_id_nf = models.BigIntegerField(null=True)
    i_path_nf = models.FloatField(default=99999.9)
    i_path_id_nf = models.BigIntegerField(null=True)
    e_path_nf = models.FloatField(default=99999.9)
    e_path_id_nf = models.BigIntegerField(null=True)

    b_time_ng = models.DecimalField(max_digits=6, decimal_places=3, default=999.999)
    b_time_id_ng = models.BigIntegerField(null=True)
    i_time_ng = models.DecimalField(max_digits=6, decimal_places=3, default=999.999)
    i_time_id_ng = models.BigIntegerField(null=True)
    e_time_ng = models.DecimalField(max_digits=6, decimal_places=3, default=999.999)
    e_time_id_ng = models.BigIntegerField(null=True)
    b_bvs_ng = models.FloatField(default=0.0)
    b_bvs_id_ng = models.BigIntegerField(null=True)
    i_bvs_ng = models.FloatField(default=0.0)
    i_bvs_id_ng = models.BigIntegerField(null=True)
    e_bvs_ng = models.FloatField(default=0.0)
    e_bvs_id_ng = models.BigIntegerField(null=True)
    b_stnb_ng = models.FloatField(default=0.0)
    b_stnb_id_ng = models.BigIntegerField(null=True)
    i_stnb_ng = models.FloatField(default=0.0)
    i_stnb_id_ng = models.BigIntegerField(null=True)
    e_stnb_ng = models.FloatField(default=0.0)
    e_stnb_id_ng = models.BigIntegerField(null=True)
    b_ioe_ng = models.FloatField(default=0.0)
    b_ioe_id_ng = models.BigIntegerField(null=True)
    i_ioe_ng = models.FloatField(default=0.0)
    i_ioe_id_ng = models.BigIntegerField(null=True)
    e_ioe_ng = models.FloatField(default=0.0)
    e_ioe_id_ng = models.BigIntegerField(null=True)
    b_path_ng = models.FloatField(default=99999.9)
    b_path_id_ng = models.BigIntegerField(null=True)
    i_path_ng = models.FloatField(default=99999.9)
    i_path_id_ng = models.BigIntegerField(null=True)
    e_path_ng = models.FloatField(default=99999.9)
    e_path_id_ng = models.BigIntegerField(null=True)

    b_time_dg = models.DecimalField(max_digits=6, decimal_places=3, default=999.999)
    b_time_id_dg = models.BigIntegerField(null=True)
    i_time_dg = models.DecimalField(max_digits=6, decimal_places=3, default=999.999)
    i_time_id_dg = models.BigIntegerField(null=True)
    e_time_dg = models.DecimalField(max_digits=6, decimal_places=3, default=999.999)
    e_time_id_dg = models.BigIntegerField(null=True)
    b_bvs_dg = models.FloatField(default=0.0)
    b_bvs_id_dg = models.BigIntegerField(null=True)
    i_bvs_dg = models.FloatField(default=0.0)
    i_bvs_id_dg = models.BigIntegerField(null=True)
    e_bvs_dg = models.FloatField(default=0.0)
    e_bvs_id_dg = models.BigIntegerField(null=True)
    b_stnb_dg = models.FloatField(default=0.0)
    b_stnb_id_dg = models.BigIntegerField(null=True)
    i_stnb_dg = models.FloatField(default=0.0)
    i_stnb_id_dg = models.BigIntegerField(null=True)
    e_stnb_dg = models.FloatField(default=0.0)
    e_stnb_id_dg = models.BigIntegerField(null=True)
    b_ioe_dg = models.FloatField(default=0.0)
    b_ioe_id_dg = models.BigIntegerField(null=True)
    i_ioe_dg = models.FloatField(default=0.0)
    i_ioe_id_dg = models.BigIntegerField(null=True)
    e_ioe_dg = models.FloatField(default=0.0)
    e_ioe_id_dg = models.BigIntegerField(null=True)
    b_path_dg = models.FloatField(default=99999.9)
    b_path_id_dg = models.BigIntegerField(null=True)
    i_path_dg = models.FloatField(default=99999.9)
    i_path_id_dg = models.BigIntegerField(null=True)
    e_path_dg = models.FloatField(default=99999.9)
    e_path_id_dg = models.BigIntegerField(null=True)

    def __str__(self):
        return 'user {}'.format(self.user.username)

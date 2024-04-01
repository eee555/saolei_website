from django.db import models
# from userprofile.models import UserProfile

def get_default_designators():
    return []

def RTimeField():
    models.DecimalField(max_digits=6, decimal_places=3, default=999.999)
def BBBVsField():
    models.FloatField(default=0.0)
def STNBField():
    models.FloatField(default=0.0)
def IOEField():
    models.FloatField(default=0.0)
def PathField():
    models.FloatField(default=99999.9)

def VideoIDField():
    models.BigIntegerField(null=True)
def VideoCountField():
    models.IntegerField(null=False, default=0)

# 扫雷用户
class UserMS(models.Model):
    # 用户的标识。管理员审核通过后可以自由使用该标识。
    designators = models.JSONField(default=get_default_designators)
    # 总录像数限制默认100，计划管理员可以修改。高水平玩家也可以增多。
    # 高级标准sub100是200；sub60是500；sub50是600；sub40是800；sub30是1000；vip是1000。
    video_num_limit = models.IntegerField(null=False, default=100)
    
    # 录像计数
    video_num_total = VideoCountField() # 录像总数
    video_num_beg   = VideoCountField() # 初级
    video_num_int   = VideoCountField() # 中级
    video_num_exp   = VideoCountField() # 高级
    video_num_std   = VideoCountField() # 标准
    video_num_nf    = VideoCountField() # 盲扫
    video_num_ng    = VideoCountField() # 无猜
    video_num_dg    = VideoCountField() # 递归

    # 标准、盲扫、无猜、递归的记录
    b_time_std = RTimeField()
    b_time_id_std = VideoIDField()
    i_time_std = RTimeField()
    i_time_id_std = VideoIDField()
    e_time_std = RTimeField()
    e_time_id_std = VideoIDField()
    b_bvs_std = BBBVsField()
    b_bvs_id_std = VideoIDField()
    i_bvs_std = BBBVsField()
    i_bvs_id_std = VideoIDField()
    e_bvs_std = BBBVsField()
    e_bvs_id_std = VideoIDField()
    b_stnb_std = STNBField()
    b_stnb_id_std = VideoIDField()
    i_stnb_std = STNBField()
    i_stnb_id_std = VideoIDField()
    e_stnb_std = STNBField()
    e_stnb_id_std = VideoIDField()
    b_ioe_std = IOEField()
    b_ioe_id_std = VideoIDField()
    i_ioe_std = IOEField()
    i_ioe_id_std = VideoIDField()
    e_ioe_std = IOEField()
    e_ioe_id_std = VideoIDField()
    b_path_std = PathField()
    b_path_id_std = VideoIDField()
    i_path_std = PathField()
    i_path_id_std = VideoIDField()
    e_path_std = PathField()
    e_path_id_std = VideoIDField()

    b_time_nf = RTimeField()
    b_time_id_nf = VideoIDField()
    i_time_nf = RTimeField()
    i_time_id_nf = VideoIDField()
    e_time_nf = RTimeField()
    e_time_id_nf = VideoIDField()
    b_bvs_nf = BBBVsField()
    b_bvs_id_nf = VideoIDField()
    i_bvs_nf = BBBVsField()
    i_bvs_id_nf = VideoIDField()
    e_bvs_nf = BBBVsField()
    e_bvs_id_nf = VideoIDField()
    b_stnb_nf = STNBField()
    b_stnb_id_nf = VideoIDField()
    i_stnb_nf = STNBField()
    i_stnb_id_nf = VideoIDField()
    e_stnb_nf = STNBField()
    e_stnb_id_nf = VideoIDField()
    b_ioe_nf = IOEField()
    b_ioe_id_nf = VideoIDField()
    i_ioe_nf = IOEField()
    i_ioe_id_nf = VideoIDField()
    e_ioe_nf = IOEField()
    e_ioe_id_nf = VideoIDField()
    b_path_nf = PathField()
    b_path_id_nf = VideoIDField()
    i_path_nf = PathField()
    i_path_id_nf = VideoIDField()
    e_path_nf = PathField()
    e_path_id_nf = VideoIDField()

    b_time_ng = RTimeField()
    b_time_id_ng = VideoIDField()
    i_time_ng = RTimeField()
    i_time_id_ng = VideoIDField()
    e_time_ng = RTimeField()
    e_time_id_ng = VideoIDField()
    b_bvs_ng = BBBVsField()
    b_bvs_id_ng = VideoIDField()
    i_bvs_ng = BBBVsField()
    i_bvs_id_ng = VideoIDField()
    e_bvs_ng = BBBVsField()
    e_bvs_id_ng = VideoIDField()
    b_stnb_ng = STNBField()
    b_stnb_id_ng = VideoIDField()
    i_stnb_ng = STNBField()
    i_stnb_id_ng = VideoIDField()
    e_stnb_ng = STNBField()
    e_stnb_id_ng = VideoIDField()
    b_ioe_ng = IOEField()
    b_ioe_id_ng = VideoIDField()
    i_ioe_ng = IOEField()
    i_ioe_id_ng = VideoIDField()
    e_ioe_ng = IOEField()
    e_ioe_id_ng = VideoIDField()
    b_path_ng = PathField()
    b_path_id_ng = VideoIDField()
    i_path_ng = PathField()
    i_path_id_ng = VideoIDField()
    e_path_ng = PathField()
    e_path_id_ng = VideoIDField()

    b_time_dg = RTimeField()
    b_time_id_dg = VideoIDField()
    i_time_dg = RTimeField()
    i_time_id_dg = VideoIDField()
    e_time_dg = RTimeField()
    e_time_id_dg = VideoIDField()
    b_bvs_dg = BBBVsField()
    b_bvs_id_dg = VideoIDField()
    i_bvs_dg = BBBVsField()
    i_bvs_id_dg = VideoIDField()
    e_bvs_dg = BBBVsField()
    e_bvs_id_dg = VideoIDField()
    b_stnb_dg = STNBField()
    b_stnb_id_dg = VideoIDField()
    i_stnb_dg = STNBField()
    i_stnb_id_dg = VideoIDField()
    e_stnb_dg = STNBField()
    e_stnb_id_dg = VideoIDField()
    b_ioe_dg = IOEField()
    b_ioe_id_dg = VideoIDField()
    i_ioe_dg = IOEField()
    i_ioe_id_dg = VideoIDField()
    e_ioe_dg = IOEField()
    e_ioe_id_dg = VideoIDField()
    b_path_dg = PathField()
    b_path_id_dg = VideoIDField()
    i_path_dg = PathField()
    i_path_id_dg = VideoIDField()
    e_path_dg = PathField()
    e_path_id_dg = VideoIDField()

    def __str__(self):
        return 'designators: {}'.format(self.designators)

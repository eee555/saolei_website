from django.db.models import TextChoices


class MS_TextChoices:
    class Mode(TextChoices):
        STD = '00', ('标准')
        UPK = '01', ('upk')
        WQ = '04', ('win7')
        JSW = '05', ('竞速无猜')
        QWC = '06', ('强无猜')
        RWC = '07', ('弱无猜')
        ZWC = '08', ('准无猜')
        QKC = '09', ('强可猜')
        RKC = '10', ('弱可猜')
        BZD = '11', ('标准递归')
        NF = '12', ('标准盲扫')

    class Level(TextChoices):
        BEGINNER = "b", ('初级')
        INTERMEDIATE = "i", ('中级')
        EXPERT = "e", ('高级')
        CUSTOM = "c", ('自定义')

    class State(TextChoices):
        PLAIN = "a", ('已上传但未审核')
        FROZEN = "b", ('审核未通过，被冻结')
        OFFICIAL = "c", ('已通过审核')
        IDENTIFIER = "d", ('标识不匹配')


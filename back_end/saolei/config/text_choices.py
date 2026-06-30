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
        BEGINNER = 'b', ('初级')
        INTERMEDIATE = 'i', ('中级')
        EXPERT = 'e', ('高级')
        CUSTOM_8_8_20 = 'c8_8_20', ('8x8 20雷')
        CUSTOM_8_8_24 = 'c8_8_24', ('8x8 24雷')
        CUSTOM_8_8_28 = 'c8_8_28', ('8x8 28雷')
        CUSTOM_8_8_32 = 'c8_8_32', ('8x8 32雷')
        CUSTOM_8_8_36 = 'c8_8_36', ('8x8 36雷')
        CUSTOM_8_8_40 = 'c8_8_40', ('8x8 40雷')
        CUSTOM_16_16_64 = 'c16_16_64', ('16x16 64雷')
        CUSTOM_16_16_80 = 'c16_16_80', ('16x16 80雷')
        CUSTOM_16_16_96 = 'c16_16_96', ('16x16 96雷')
        CUSTOM_16_16_112 = 'c16_16_112', ('16x16 112雷')
        CUSTOM_16_16_128 = 'c16_16_128', ('16x16 128雷')
        CUSTOM_16_30_120 = 'c16_30_120', ('16x30 120雷')
        CUSTOM_16_30_144 = 'c16_30_144', ('16x30 144雷')
        CUSTOM_16_30_168 = 'c16_30_168', ('16x30 168雷')
        CUSTOM_16_30_192 = 'c16_30_192', ('16x30 192雷')
        CUSTOM_24_30_180 = 'c24_30_180', ('24x30 180雷')
        CUSTOM_24_30_216 = 'c24_30_216', ('24x30 216雷')
        CUSTOM_24_30_252 = 'c24_30_252', ('24x30 252雷')
        CUSTOM_48_64_777 = 'c48_64_777', ('48x64 777雷')

    class State(TextChoices):
        PLAIN = 'a', ('已上传但未审核')
        FROZEN = 'b', ('审核未通过，被冻结')
        OFFICIAL = 'c', ('已通过审核')
        IDENTIFIER = 'd', ('标识不匹配')
        EXTERNAL = 'e', ('外部网站审核')

    class Software(TextChoices):
        AVF = 'a', ('avf')
        EVF = 'e', ('evf')
        MVF = 'm', ('mvf')
        RMV = 'r', ('rmv')


class Saolei_TextChoices:
    class SaoleiVideoState(TextChoices):
        NOTEXIST = 'n', ('不存在')
        PENDING = 'p', ('未审核')
        FROZEN = 'f', ('已冻结')
        OFFICIAL = 'o', ('正常')

    class SaoleiVideoImportState(TextChoices):
        NOTPLANNED = 'n', ('未计划')
        READY = 'r', ('准备就绪')
        QUEUEING = 'q', ('排队中')
        IMPORTING = 'i', ('导入中')
        IMPORTED = 'd', ('已导入')
        FAILED = 'f', ('导入失败')


class Tournament_TextChoices:
    class Series(TextChoices):
        WEEKLY = 'w', ('周赛')
        GSC = 'g', ('GSC')

    class State(TextChoices):
        PENDING = 'p', ('审核中')
        ONGOING = 'o', ('进行中')
        FINISHED = 'f', ('已结束')
        PREPARING = 'r', ('准备中')
        CANCELLED = 'c', ('已取消')
        AWARDED = 'a', ('已颁奖')

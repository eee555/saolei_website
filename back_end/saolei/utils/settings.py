# 数据大小限制
class MaxSizes:
    avatar = 1024*300 # 头像图片
    country = 2 # Alpha-2 code from ISO3166
    email = 100
    emailcaptcha = 6 # 邮箱验证码
    firstname = 10
    lastname = 10
    signature = 188
    username = 20
    videofile = 5242800 # 录像文件

# 默认修改个人资料的次数
class DefaultChances:
    name = 1 # 名字
    avatar = 2 # 头像
    signature = 2 # 签名
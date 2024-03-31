# 数据大小限制
class MinSizes:
    password = 6

class MaxSizes:
    avatar = 1024*300 # 头像图片
    country = 2 # Alpha-2 code from ISO3166
    email = 100
    emailcaptcha = 6 # 邮箱验证码
    firstname = 10
    gamelevel = 1 # 级别（初中高）
    gamemode = 2 # 模式（无猜）
    gametime = 6 # 时间（毫秒）
    lastname = 10
    password = 20 # 密码
    signature = 188
    software = 1
    username = 20 # 用户名
    videofile = 5*1024*1024 # 录像文件

# 默认修改个人资料的次数
class DefaultChances:
    name = 1 # 名字
    avatar = 2 # 头像
    signature = 2 # 签名

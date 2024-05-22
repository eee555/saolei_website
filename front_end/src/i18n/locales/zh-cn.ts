import { LocaleConfig } from '@/i18n/config'

export const zhCn: LocaleConfig = {
    local: 'zh-cn',
    name: '简体中文',
    common: {
        time: '用时'
    },
    menu: {
        ranking: '排行',
        statistics: '统计',
        profile: '我的',
        video: '录像库',
        login: '登录',
        register: '注册'
    },
    login: {
        title: '欢迎登录',
        username: '用户名',
        password: '密码',
        logout: '退出',
        captcha: '验证码',
        forgetPassword: '（找回密码）',
        keepMeLoggedIn: '记住我',
        confirm: '登录'
    },
    register: {
        title: '用户注册',
        username: '请输入用户昵称（唯一、登录凭证、无法修改）',
        email: '请输入邮箱（唯一）',
        captcha: '验证码',
        getEmailCode: '获取邮箱验证码',
        emailCode: '请输入邮箱验证码',
        password: '请输入6-20位密码',
        confirmPassword: '请输入确认密码',
        agreeTo: '已阅读并同意',
        termsAndConditions: '元扫雷网用户协议',
        confirm: '注册'
    },
    example: {
        placeholder: '占位符: {0}',
    },
}

import { LocaleConfig } from '@/i18n/config'

export const dev: LocaleConfig = {
    local: 'dev',
    name: 'name',
    common: {
        time: 'common.time'
    },
    menu: {
        ranking: 'menu.ranking',
        statistics: 'menu.statistics',
        profile: 'menu.profile',
        video: 'menu.video',
        login: 'menu.login',
        register: 'menu.register'
    },
    login: {
        title: 'login.title',
        username: 'login.username',
        password: 'login.password',
        logout: 'login.logout',
        captcha: 'login.captcha',
        forgetPassword: 'login.forgetPassword',
        keepMeLoggedIn: 'login.keepMeLoggedIn',
        confirm: 'login.confirm'
    },
    register: {
        title: 'register.title',
        username: 'register.username',
        email: 'register.email',
        captcha: 'register.captcha',
        getEmailCode: 'register.getEmailCode',
        emailCode: 'register.emailCode',
        password: 'register.password',
        confirmPassword: 'register.confirmPassword',
        agreeTo: 'register.agreeTo',
        termsAndConditions: 'register.termsAndConditions',
        confirm: 'register.confirm'
    },
    example: {
        placeholder: 'example.placeholder: {0}',
    },
}
import type { VueMessageType } from 'vue-i18n'
import { LocaleMessage } from '@intlify/core-base'

/**
 * 配置语法：https://vue-i18n.intlify.dev/guide/essentials/syntax.html
 */
export type LocaleConfig = LocaleMessage<VueMessageType> & {
    // 当前语言唯一标识
    local: string,
    // 嵌套配置示例 TODO 删除嵌套配置示例
    name: string,
    common: {
        time: string
    },
    menu: {
        ranking: string,
        statistics: string,
        profile: string,
        video: string,
        login: string,
        register: string
    },
    login: {
        title: string,
        username: string,
        password: string,
        logout: string,
        captcha: string,
        forgetPassword: string,
        keepMeLoggedIn: string,
        confirm: string
    },
    register: {
        title: string,
        username: string,
        email: string,
        captcha: string,
        getEmailCode: string,
        emailCode: string,
        password: string,
        confirmPassword: string,
        agreeTo: string,
        termsAndConditions: string,
        confirm: string
    },
    example: {
        // 占位符配置示例 TODO 删除占位符配置示例
        placeholder: string
    }
}

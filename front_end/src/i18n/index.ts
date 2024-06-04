import { createI18n } from 'vue-i18n'
import { dev } from '@/i18n/locales/dev'
import { zhCn } from '@/i18n/locales/zh-cn'
import { de } from '@/i18n/locales/de'
import { en } from './locales/en'
import { LocaleConfig } from '@/i18n/config'

/**
 * 获取所有语言
 */
function getMessages (): Record<string, any> {
    const messages: Record<string, any> = {}
    messages[dev.local] = dev
    messages[zhCn.local] = zhCn
    messages[de.local] = de
    messages[en.local] = en
    return messages
}

/**
 * 获取默认语言
 */
function getDefaultLocale () {
    const languages = navigator.languages || [navigator.language]
    for (const language of languages) {
        if (/^zh(.?CN)?$/i.test(language)) {
            // 简体中文，包括 zh 和 zh-CN
            return zhCn.local
        } else if (language == de.local) {
            return de.local
        } else if (language == en.local) {
            return en.local
        }
    }
    // 默认使用简体中文
    return dev.local
}

/**
 * 配置 Vue I18n，开发工具参见：https://vue-i18n.intlify.dev/ecosystem/tools.html
 */
export default createI18n({
    legacy: false,
    fallbackLocale: dev.local,
    fallbackWarn: false,
    missingWarn: false,
    locale: getDefaultLocale(),
    messages: getMessages(),
})

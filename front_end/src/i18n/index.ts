import { createI18n } from 'vue-i18n'
import { dev } from '@/i18n/locales/dev'
import { zhCn } from '@/i18n/locales/zh-cn'
import { de } from '@/i18n/locales/de'
import { en } from './locales/en'
import { pl } from './locales/pl'

/**
 * 获取所有语言
 */
function getMessages (): Record<string, any> {
    const messages: Record<string, any> = {}
    messages[dev.local] = dev
    messages[zhCn.local] = zhCn
    messages[de.local] = de
    messages[en.local] = en
    messages[pl.local] = pl
    return messages
}

/**
 * 获取默认语言
 */
function getDefaultLocale () {
    return "en"
}

/**
 * 配置 Vue I18n，开发工具参见：https://vue-i18n.intlify.dev/ecosystem/tools.html
 */
export default createI18n({
    legacy: false,
    fallbackLocale: {
        'zh-cn': ['dev'],
        'en': ['dev'],
        'de': ['en'],
        'pl': ['en'],
    },
    fallbackWarn: false,
    missingWarn: false,
    warnHtmlMessage: false,
    locale: getDefaultLocale(),
    messages: getMessages(),
})

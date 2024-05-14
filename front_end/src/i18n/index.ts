import { createI18n } from 'vue-i18n'
import { en } from '@/i18n/locales/en'
import { zhCn } from '@/i18n/locales/zh-cn'
import { zhTw } from '@/i18n/locales/zh-tw'
import { LocaleConfig } from '@/i18n/config'

/**
 * 获取所有语言
 */
function getMessages (): Record<string, LocaleConfig> {
    const messages: Record<string, LocaleConfig> = {}
    messages[zhCn.local] = zhCn
    messages[zhTw.local] = zhTw
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
        } else if (/^zh\b/i.test(language)) {
            // 除简体中文外的所有中文默认使用繁体中文
            return zhTw.local
        } else if (/^en\b/i.test(language)) {
            // 英语
            return en.local
        }
    }
    // 默认使用简体中文
    return zhCn.local
}

/**
 * 配置 Vue I18n，开发工具参见：https://vue-i18n.intlify.dev/ecosystem/tools.html
 */
export default createI18n({
    legacy: false,
    fallbackLocale: zhCn.local,
    locale: getDefaultLocale(),
    messages: getMessages(),
})

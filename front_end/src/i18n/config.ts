import type { VueMessageType } from 'vue-i18n'
import { LocaleMessage } from '@intlify/core-base'

/**
 * 配置语法：https://vue-i18n.intlify.dev/guide/essentials/syntax.html
 */
export type LocaleConfig = LocaleMessage<VueMessageType> & {
    // 当前语言唯一标识
    local: string
    // 嵌套配置示例 TODO 删除嵌套配置示例
    example: {
        // 占位符配置示例 TODO 删除占位符配置示例
        placeholder: string
    }
}

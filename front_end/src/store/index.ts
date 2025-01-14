import { LoginStatus } from "@/utils/common/structInterface"
import { defineStore } from 'pinia'
import { pinia } from "./create"
import { useLocalStorage } from "@vueuse/core"
import { colorSchemeTemplates } from "@/utils/config"
import { UserProfile } from "@/utils/userprofile"

export const store = defineStore('user', {
    state: () => ({
        user: new UserProfile(),   // 真正的用户
        // 访问谁的地盘不再具有记忆性。即点“我的地盘”，将永远是“我”的地盘
        // 想要访问特定用户，可以用url
        // 访问谁的地盘
        player: new UserProfile(),
        login_status: LoginStatus.Undefined, // 登录状态，全局维护
        new_identifier: false, // 是否有新标识录像
    }),
})(pinia)

export const videoplayerstore = defineStore('videoplayer', {
    state: () => ({
        visible: false,
        id: 0,
    }),
})(pinia)

export const local = useLocalStorage('local', {
    darkmode: false,
    experimental: false,
    language: (navigator.language).toLocaleLowerCase(),
    language_show: true,
    menu_font_size: 18,
    menu_height: 60,
    menu_icon: false,
    notification_duration: 4500,
    tooltip_show: true,
})

export const videofilter = useLocalStorage('videofilter', {
    pagesize: 100,
    level: 'e',
    filter_state: ['a', 'b', 'c', 'd'],
    bbbv_range: {
        'b': [2, 54],
        'i': [30, 216],
        'e': [100, 381],
    }
})

export const colorTheme = useLocalStorage('colorTheme', colorSchemeTemplates.ArbiterStatsAuto)

export const activityCalendarConfig = useLocalStorage('activity-calendar-config', {
    cellSize: 14,
    cellMargin: 3,
    cornerRadius: 20,
    showDate: false,
})
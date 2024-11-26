import { LoginStatus } from "@/utils/common/structInterface"
import { defineStore } from 'pinia'
import { pinia } from "./create"

export const store = defineStore('user', {
    state: () => ({
        user: {
            // 此id为用户的id从1开始，而不是数据库的自增id
            id: 0,
            username: "",
            realname: "",
            is_banned: false,
            is_staff: false,
            country: "",
            accountlink: [],
            identifiers: [],
            videos: [],
            loading: true,
        },   // 真正的用户
        // 访问谁的地盘不再具有记忆性。即点“我的地盘”，将永远是“我”的地盘
        // 想要访问特定用户，可以用url
        // 访问谁的地盘
        player: {
            // 此id为用户的id从1开始，而不是数据库的自增id
            id: 0,
            username: "",
            realname: "",
            is_banned: false,
            is_staff: false,
            country: "",
            accountlink: [] as any[],
            identifiers: [] as string[],
            videos: [] as any[],
            loading: true,
        },
        login_status: LoginStatus.Undefined, // 登录状态，全局维护
        new_identifier: false, // 是否有新标识录像
    }
    ),
})(pinia)

export const videoplayerstore = defineStore('videoplayer', {
    state: () => ({
        visible: false,
        id: 0,
    }),
})(pinia)

export const local = defineStore('local', {
    state: () => ({
        darkmode: false,
        language: (navigator.language).toLocaleLowerCase(),
        language_show: true,
        menu_font_size: 18,
        menu_height: 60,
        menu_icon: false,
        notification_duration: 4500,
        tooltip_show: true,
    }),
    persist: true,
})(pinia)

export const videofilter = defineStore('videofilter', {
    state: () => ({
        pagesize: 100,
        level: 'e',
        filter_state: ['a','b','c','d'],
        bbbv_range: {
            'b': [2,54],
            'i': [30,216],
            'e': [100,381],
        }
    }),
    persist: true
})(pinia)
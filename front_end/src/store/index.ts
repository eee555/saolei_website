import { LoginStatus } from "@/utils/common/structInterface"
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
    state: () => ({
        user: {
            // 此id为用户的id从1开始，而不是数据库的自增id
            id: 0,
            username: "",
            realname: "",
            is_banned: false,
            is_staff: false,
            country: ""
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
            country: ""
        },
        // 登录状态，全局维护
        login_status: LoginStatus.Undefined,
    }
    ),
})

export const useLocalStore = defineStore('local', {
    state: () => ({
        language: "zh-cn",
        language_show: true,
        menu_icon: false,
    }),
    persist: true,
})
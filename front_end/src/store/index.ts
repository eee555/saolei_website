import { useLocalStorage } from '@vueuse/core';
import { defineStore } from 'pinia';

import { pinia } from './create';

import { deepMutableCopy } from '@/utils';
import { LoginStatus } from '@/utils/common/structInterface';
import { colorSchemeTemplates } from '@/utils/config';
import type { CellChoice, ColorTemplateName, ColumnChoice, MS_Software } from '@/utils/ms_const';
import { MS_Softwares, MS_State } from '@/utils/ms_const';
import type { Tournament } from '@/utils/tournaments';
import { UserProfile } from '@/utils/userprofile';
import type { getStat_stat, VideoAbstract } from '@/utils/videoabstract';

export const store = defineStore('user', {
    state: () => ({
        user: new UserProfile(), // 真正的用户
        // 访问谁的地盘不再具有记忆性。即点“我的地盘”，将永远是“我”的地盘
        // 想要访问特定用户，可以用url
        // 访问谁的地盘
        player: new UserProfile(),
        login_status: LoginStatus.Undefined, // 登录状态，全局维护
        new_identifier: false, // 是否有新标识录像
        video_list: [] as VideoAbstract[],
        video_list_show: false,
        tournamentTabs: [] as Tournament[],
    }),
    getters: {
        isSelf: (state) => state.user.id === state.player.id && state.user.id !== 0,
        isUserAnonymous: (state) => state.user.realname === '',
        expTimeMs: (state) => {
            let ret = 999999;
            if (!state.user.videos) return ret;
            for (const video of state.user.videos) {
                if (video.state === MS_State.Official && video.level === 'e') {
                    ret = Math.min(ret, video.timems);
                }
            }
            return ret;
        },
    },
    actions: {
        login(userdata: any) {
            this.user = new UserProfile(userdata);
            this.login_status = LoginStatus.IsLogin;
        },
        logout() {
            this.user = new UserProfile();
            this.login_status = LoginStatus.NotLogin;
        },
    },
})(pinia);

export const videoplayerstore = defineStore('videoplayer', {
    state: () => ({
        visible: false,
        id: 0,
        software: 'a' as MS_Software,
        url: '',
        error: null as any,
    }),
})(pinia);

export const local = useLocalStorage(
    'local',
    {
        darkmode: matchMedia('(prefers-color-scheme: dark)').matches,
        experimental: false,
        language: navigator.language.toLocaleLowerCase(),
        language_show: true,
        menu_font_size: 18,
        menu_height: 60,
        menu_icon: false,
        notification_duration: 4500,
        tooltip_show: true,
        vienna_logo_legacy: false,
        autoUploadAfterParse: false,
        autoRemoveAfterUpload: false,
        folderMonitorPollingInterval: 3000,
        nameFormat: 'first-last' as 'first-last' | 'last-first',
    },
    { mergeDefaults: true },
);

export const videoPlayerConfig = useLocalStorage(
    'video-player-config',
    {
        backend: 'flop' as 'flop' | 'StrangeDust',
        strangeDustTrust: false,
    },
    { mergeDefaults: true },
);

export const videofilter = useLocalStorage('videofilter', {
    pagesize: 100,
    level: 'e',
    filter_state: ['a', 'b', 'c', 'd'],
    bbbv_range: {
        b: [2, 54],
        i: [30, 216],
        e: [100, 381],
    },
});

export const colorTheme = useLocalStorage(
    'colorTheme',
    {
        ...deepMutableCopy(colorSchemeTemplates.ArbiterStatsAuto),
        level: {
            b: '#dc2626',
            i: '#16a34a',
            e: '#2563eb',
        },
    },
    { mergeDefaults: true },
);

export const activityCalendarConfig = useLocalStorage(
    'activity-calendar-config',
    {
        cellSize: 14,
        cellMargin: 3,
        cornerRadius: 20,
        showDate: false,
        useEndTime: false,
    },
    { mergeDefaults: true },
);

export const BBBvSummaryConfig = useLocalStorage(
    'bbbv-summary-config',
    {
        template: 'time' as ColorTemplateName,
        sortBy: 'timems' as getStat_stat,
        displayBy: 'time' as CellChoice,
        sortDesc: false,
        softwareFilter: [...MS_Softwares] as MS_Software[],
        zoom: 1,
        tooltipMode: 'fast' as 'fast' | 'advanced',
        showIcon: 'software' as '' | 'software' | 'state',
        newThresh: 1,
        newDateField: 'upload_time' as 'upload_time' | 'end_time',
    },
    { mergeDefaults: true },
);

export const VideoScatterAxisChoice = ['time', 'bv', 'bvs', 'stnb', 'ioe', 'thrp', 'corr', 'ces', 'cls', 'cl', 'ce', 'rqp'] as const;
export type VideoScatterAxisChoice = typeof VideoScatterAxisChoice[number];
export const VideoScatterColorByChoice = ['level', 'time', 'bvs', 'stnb', 'ioe', 'thrp', 'ces', 'cls'] as const;
export type VideoScatterColorByChoice = typeof VideoScatterColorByChoice[number];
export const VideoScatterConfig = useLocalStorage(
    'video-scatter-config',
    {
        radius: 3,
        x: 'bv' as VideoScatterAxisChoice,
        y: 'time' as VideoScatterAxisChoice,
        colorBy: 'level' as VideoScatterColorByChoice,
        highlightSelected: false,
        showOnlySelected: false,
    },
    { mergeDefaults: true },
);

export const VideoListConfig = useLocalStorage(
    'video-list-config',
    {
        profile: ['state', 'upload_time', 'software', 'level', 'mode', 'time', 'bv', 'bvs', 'ioe', 'thrp', 'path', 'file_size'] as ColumnChoice[],
        tournament: ['state', 'upload_time', 'software', 'level', 'mode', 'time', 'bv', 'bvs', 'ioe', 'thrp', 'path'] as ColumnChoice[],
    },
    { mergeDefaults: true },
);

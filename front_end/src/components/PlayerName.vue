<template>
    <span @click.stop>
        <Tippy
            trigger="click"
            interactive
            :duration="0"
            :max-width="298"
            :append-to="getAppendTarget"
            placement="bottom"
            :on-shown="pop_show"
            :on-hide="pop_hide"
        >
            <ElLink underline="never">
                <PlayerBadge :user-id="userId" :name="nameShown" />
            </ElLink>
            <template #content>
                <ElCard class="card-small">
                    <div style="width: 80px;float: left;line-height: 200%;">
                        <UserAvatar :user-id="userId" />
                        <ElButton tag="a" :href="playerProfileHref" style="width: 72px; height: 24px; text-decoration: none;">
                            {{ t('local.visitMe') }}
                        </ElButton>
                    </div>
                    <div style="width: 188px; float: right; text-align: center;line-height: 180%;">
                        <div>
                            <span v-if="user.isAnonymous">
                                {{ t('common.anonymous') }}
                            </span>
                            <span v-else>
                                {{ user.realname }}
                            </span>
                            <span v-if="user.hasInternationalName">
                                ({{ formatName(user.firstname, user.lastname, local.nameFormat) }})
                            </span>
                            <span>
                                #{{ userId }}
                            </span>
                        </div>
                        <div v-loading="is_loading" class="record-table">
                            <template v-for="(record, level) in records">
                                <div>
                                    {{ t(`common.level.short${level}`) }}
                                </div>
                                <div>
                                    <PreviewNumber :id="record.timems_id ?? 0" :text="ms_to_s(record.timems)" />
                                </div>
                                <div>
                                    <PreviewNumber :id="record.bvs_id ?? 0" :text="to_fixed_n(record.bvs, 3)" />
                                </div>
                            </template>
                            <div>
                                {{ t('common.level.sum') }}
                            </div>
                            <div style="color: #BF9000;font-weight: bold;">
                                {{ ms_to_s(records.b.timems + records.i.timems + records.e.timems) }}
                            </div>
                            <div style="color: #BF9000;font-weight: bold;">
                                {{ to_fixed_n(records.b.bvs + records.i.bvs + records.e.bvs, 3) }}
                            </div>
                        </div>
                    </div>
                </ElCard>
            </template>
        </Tippy>
    </span>
</template>

<script setup lang="ts" name="PlayerName">
// 用户的名字，鼠标移上去以后弹出气泡框，可以访问他的主页
import '@/styles/cards.css';

import { ElButton, ElCard, ElLink, vLoading } from 'element-plus';
import { computed, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { Tippy } from 'vue-tippy';

import PreviewNumber from '@/components/PreviewNumber.vue';
import PlayerBadge from '@/components/widgets/PlayerBadge.vue';
import UserAvatar from '@/components/widgets/UserAvatar.vue';
import type { UserRecordLevel, UserRecordsAbstractResponse } from '@/services/msuserService';
import { fetchPlayerRecordsAbstract } from '@/services/msuserService';
import { fetchUserInfo } from '@/services/userService';
import { local } from '@/store';
import { createEnumMap, ms_to_s, to_fixed_n } from '@/utils';
import { formatName } from '@/utils/strings';
import { UserProfile } from '@/utils/userprofile';

const props = defineProps({
    userId: {
        type: Number,
        default: 0,
    },
});

const user = ref(new UserProfile());
const loading = ref(false);
const nameShown = computed(() => {
    if (loading.value) {
        return `${t('local.user')}#${props.userId}`;
    } else {
        return user.value.realname;
    }
});
const playerProfileHref = computed(() => `#/player/${props.userId}`);
const getAppendTarget = () => document.body;

watch(() => props.userId, async (newVal) => {
    user.value = new UserProfile();
    if (newVal === 0) return;
    else {
        loading.value = true;
        try {
            user.value = await fetchUserInfo(props.userId);
            loading.value = false;
        } catch (error) {
            user.value = new UserProfile();
            console.log(error);
        }
    }
}, { immediate: true });

const is_loading = ref(true);

interface PlayerNameRecord {
    timems: number;
    bvs: number;
    timems_id: number | null;
    bvs_id: number | null;
}

const recordLevels = ['b', 'i', 'e'] as const;

const defaultRecord: PlayerNameRecord = {
    timems: 999999,
    bvs: 0,
    timems_id: null,
    bvs_id: null,
};

const records = ref(createEnumMap(recordLevels, defaultRecord));

function createRecord(data: UserRecordsAbstractResponse, level: UserRecordLevel): PlayerNameRecord {
    return {
        timems: data[`${level}_timems_std`],
        bvs: data[`${level}_bvs_std`],
        timems_id: data[`${level}_timems_id_std`],
        bvs_id: data[`${level}_bvs_id_std`],
    };
}

function setRecords(data: UserRecordsAbstractResponse) {
    records.value = {
        b: createRecord(data, 'b'),
        i: createRecord(data, 'i'),
        e: createRecord(data, 'e'),
    };
}

async function pop_show() {
    if (props.userId === 0) return;
    is_loading.value = true;

    const data = await fetchPlayerRecordsAbstract(props.userId);
    setRecords(data);

    is_loading.value = false;
}

// 用户记录小弹窗关闭后，删除其中的数据
function pop_hide() {
    records.value = createEnumMap(recordLevels, defaultRecord);
    is_loading.value = true;
}

const i18nMessages = {
    'zh-cn': { local: {
        user: '用户',
        visitMe: '我的空间',
    } },
    en: { local: {
        user: 'User',
        visitMe: 'My space',
    } },
    fr: { local: {
        visitMe: 'Mon espace',
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>

<style lang="less" scoped>
.record-table {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
}
</style>

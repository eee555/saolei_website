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
                            <div>
                                {{ t('common.level.shortb') }}
                            </div>
                            <div>
                                <PreviewNumber :id="+b_t_id" :text="ms_to_s(b_t)" />
                            </div>
                            <div>
                                <PreviewNumber :id="+b_bvs_id" :text="to_fixed_n(b_bvs, 3)" />
                            </div>
                            <div>
                                {{ t('common.level.shorti') }}
                            </div>
                            <div>
                                <PreviewNumber :id="+i_t_id" :text="ms_to_s(i_t)" />
                            </div>
                            <div>
                                <PreviewNumber :id="+i_bvs_id" :text="to_fixed_n(i_bvs, 3)" />
                            </div>
                            <div>
                                {{ t('common.level.shorte') }}
                            </div>
                            <div>
                                <PreviewNumber :id="+e_t_id" :text="ms_to_s(e_t)" />
                            </div>
                            <div>
                                <PreviewNumber :id="+e_bvs_id" :text="to_fixed_n(e_bvs, 3)" />
                            </div>
                            <div>
                                {{ t('common.level.sum') }}
                            </div>
                            <div style="color: #BF9000;font-weight: bold;">
                                {{ ms_to_s(b_t + i_t + e_t) }}
                            </div>
                            <div style="color: #BF9000;font-weight: bold;">
                                {{ to_fixed_n(b_bvs + i_bvs + e_bvs, 3) }}
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
import { fetchUserInfo } from '@/services/userService';
import { local } from '@/store';
import { ms_to_s, to_fixed_n } from '@/utils';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { formatName } from '@/utils/strings';
import { UserProfile } from '@/utils/userprofile';

const props = defineProps({
    userId: {
        type: Number,
        default: 0,
    },
});

const { proxy } = useCurrentInstance();

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

const b_t = ref(999999);
const b_bvs = ref('');
const b_t_id = ref('');
const b_bvs_id = ref('');
const i_t = ref(999999);
const i_bvs = ref('');
const i_t_id = ref('');
const i_bvs_id = ref('');
const e_t = ref(999999);
const e_bvs = ref('');
const e_t_id = ref('');
const e_bvs_id = ref('');

async function pop_show() {
    if (props.userId === 0) return;
    is_loading.value = true;

    await proxy.$axios.get('/msuser/info_abstract/',
        {
            params: {
                id: props.userId,
            },
        },
    ).then(function (response) {
        const response_data = response.data;

        const records = JSON.parse(response_data.record_abstract);

        b_t.value = records.timems[0];
        i_t.value = records.timems[1];
        e_t.value = records.timems[2];

        b_t_id.value = records.timems_id[0];
        i_t_id.value = records.timems_id[1];
        e_t_id.value = records.timems_id[2];
        b_bvs.value = records.bvs[0];
        i_bvs.value = records.bvs[1];
        e_bvs.value = records.bvs[2];
        b_bvs_id.value = records.bvs_id[0];
        i_bvs_id.value = records.bvs_id[1];
        e_bvs_id.value = records.bvs_id[2];

        is_loading.value = false;
    }).catch(() => {
        // is_loading.value = false;
    });
}

// 用户记录小弹窗关闭后，删除其中的数据
function pop_hide() {
    i_t.value = 999999;
    b_t.value = 999999;
    e_t.value = 999999;
    b_t_id.value = '';
    i_t_id.value = '';
    e_t_id.value = '';
    b_bvs.value = '';
    i_bvs.value = '';
    e_bvs.value = '';
    b_bvs_id.value = '';
    i_bvs_id.value = '';
    e_bvs_id.value = '';
    is_loading.value = true;
}

const i18nMessages = {
    'zh-cn': { local: {
        user: '用户',
        visitMe: '我的空间',
    } },
    'en': { local: {
        user: 'User',
        visitMe: 'My space',
    } },
    'fr': { local: {
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

<template>
    <span @click.stop>
        <el-popover
            v-if="render"
            :visible="visible"
            placement="bottom"
            width="298px"
            popper-class="max-h-300px overflow-auto" popper-style="z-index:888;" @show="pop_show" @hide="pop_hide"
        >
            <div>
                <div style="width: 80px;float: left;line-height: 200%;">
                    <UserAvatar :user-id="userId" />
                    <el-button style="width: 72px;height: 24px;" @click="visit_me(userId);">
                        {{ t('local.visitMe') }}
                    </el-button>
                </div>
                <div style="width: 188px;float: right;text-align: center;line-height: 180%;">
                    <div>
                        <span>
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

            </div>
            <template #reference>
                <el-link underline="never" @click="visible = !visible;">
                    <PlayerBadge :user-id="userId" :name="user.realname" />
                </el-link>
            </template>
        </el-popover>
        <el-link v-else underline="never" @click="render = true; visible = true;">
            <PlayerBadge :user-id="userId" :name="user.realname" />
        </el-link>
    </span>
</template>

<script setup lang="ts" name="PlayerName">
// 用户的名字，鼠标移上去以后弹出气泡框，可以访问他的主页
import { ElButton, ElLink, ElPopover, vLoading } from 'element-plus';
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';

import PreviewNumber from '@/components/PreviewNumber.vue';
import PlayerBadge from '@/components/widgets/PlayerBadge.vue';
import UserAvatar from '@/components/widgets/UserAvatar.vue';
import { fetchUserInfo } from '@/services/userService';
import { local } from '@/store';
import { ms_to_s, to_fixed_n } from '@/utils';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { formatName } from '@/utils/strings';
import { UserProfile } from '@/utils/userprofile';

const { proxy } = useCurrentInstance();
const router = useRouter();

const data = defineProps({
    userId: {
        type: Number,
        default: 0,
    },
});

const user = ref(new UserProfile());

watch(() => data.userId, async (newVal) => {
    if (newVal === 0) {
        user.value = new UserProfile();
    } else {
        const response = await fetchUserInfo(data.userId);
        user.value = new UserProfile(response);
    }
}, { immediate: true });

const render = ref<boolean>(false); // 控制只渲染一次
const visible = ref<boolean>(false);
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

const pop_show = async () => {
    if (data.userId === 0) return;
    document.addEventListener('mousedown', handleOutsideClick);
    is_loading.value = true;

    await proxy.$axios.get('/msuser/info_abstract/',
        {
            params: {
                id: data.userId,
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
};

// 用户记录小弹窗关闭后，删除其中的数据
const pop_hide = () => {
    document.removeEventListener('mousedown', handleOutsideClick);
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
};

const visit_me = (user_id: number) => {
    router.push({ name: 'player_id', params: { id: user_id } });
};

// 实现点旁边时候关闭气泡
const handleOutsideClick = (event: any) => {
    const componentElement = document.querySelector('.el-popover');
    if (!componentElement?.contains(event.target)) {
        visible.value = false;
    }
};

const i18nMessages = {
    'zh-cn': { local: {
        visitMe: '我的空间',
    } },
    'en': { local: {
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

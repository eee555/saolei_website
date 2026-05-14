<template>
    <input ref="fileInputRef" type="file" accept="image/jpeg,image/png,image/gif,image/webp" style="display: none" @change="handleFileChange">
    <tippy v-loading="updating">
        <el-avatar :src="avatarSrc" :disabled="disabled" @click="triggerFileDialog" />
        <template v-if="store.isSelf" #content>
            <div v-if="store.expTimeMs >= 200000">
                {{ t('local.tooltipExpTime') }}
            </div>
            <div v-else-if="avatarBudget > 0">
                {{ t('local.tooltipBase', [avatarBudget]) }}
            </div>
            <div v-else class="text">
                {{ t('local.tooltipCooldown') }}{{ toISODateTimeString(store.user.nextAvatarAvailable) }}
            </div>
        </template>
    </tippy>
</template>

<script setup lang="ts">
import '@/styles/text.css';

import { ElAvatar, vLoading } from 'element-plus';
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { Tippy } from 'vue-tippy';

import { baseErrorNotification, httpErrorNotification } from '@/components/Notifications';
import { store } from '@/store';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { globalNow, toISODateTimeString } from '@/utils/datetime';

const { proxy } = useCurrentInstance();

const props = defineProps({
    userId: { type: Number, default: 0 },
    lastUpdated: { type: Date, default: new Date() },
});

const avatarVersion = ref(0);
const avatarSrc = computed(() => `${proxy.$axios.defaults.baseURL}/api/userprofile/avatar/${props.userId}?v=${avatarVersion.value}`);

const fileInputRef = ref<HTMLInputElement>();
function triggerFileDialog() {
    if (disabled.value) return;
    fileInputRef.value!.click();
}

async function handleFileChange(event: Event) {
    updating.value = true;

    const file = (event.target as HTMLInputElement).files?.[0];
    if (!file) return;

    const maxSize = 300 * 1024;
    if (file.size > maxSize) {
        baseErrorNotification(t('local.errorTitle'), t('local.errorMsg.avatar.validation'));
        updating.value = false;
        return;
    }

    await updateAvatar(file);
    updating.value = false;
}

const avatarBudget = computed(() => store.user.newAvatarBudget(globalNow.value));

const updating = ref(false);
const disabled = computed(() => avatarBudget.value <= 0 || store.expTimeMs >= 200000);

async function updateAvatar(a: File) {
    await proxy.$axios.post('/api/userprofile/update_avatar/',
        { avatar: a },
    ).then(function (response) {
        const data = response.data;
        if (data.type === 'success') {
            avatarVersion.value++;
        } else if (data.type === 'error') {
            baseErrorNotification(t('local.errorTitle'), t(`local.errorMsg.${data.object}.${data.category}`));
        }
    }).catch(httpErrorNotification);
}

const i18nMessages = {
    'zh-cn': { local: {
        errorTitle: '头像更新失败',
        errorMsg: {
            avatar: {
                validation: '头像格式错误',
            },
            censorship: {
                unknown: '机器审核发生未知错误，请联系管理员',
                illegal: '未通过机器审核，请更换文件或联系管理员进行人工审核',
            },
        },
        tooltipBase: '点击修改头像（剩余{0}）次',
        tooltipCooldown: '头像每90天至多修改一次。下次可修改：',
        tooltipExpTime: '高级sub200后才可以修改头像',
    } },
};

const { t } = useI18n({ messages: i18nMessages });

</script>

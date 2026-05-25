<template>
    <div :class="{ 'horizontal-profile': direction === 'horizontal', 'vertical-profile': direction === 'vertical' }">
        <div class="profile">
            <div class="avatar">
                <avatar :user="user" :is-self="store.isSelf" :exp-time-ms="store.expTimeMs" />
            </div>
            <div>
                <span class="username">
                    {{ user.username }}
                </span>
                <span class="id">
                    #{{ user.id }}
                </span>
            </div>
            <div class="realname">
                {{ user.isAnonymous ? t('local.anonymous') : user.realname }}
            </div>
            <div class="fullname">
                {{ formatName(user.firstname, user.lastname, local.nameFormat) }}
            </div>
        </div>
        <el-button v-if="user.id === store.user.id" class="edit-button" @click="isEditing = true">
            {{ t('local.editButton') }}
        </el-button>
        <div class="signature">
            {{ user.signature }}
        </div>
    </div>
    <el-dialog v-model="isEditing">
        <edit-profile v-model:user="store.user" v-model:is-editing="isEditing" :exp-time-ms="store.expTimeMs" />
    </el-dialog>
</template>

<script setup lang="ts">
import { ElButton, ElDialog } from 'element-plus';
import { defineAsyncComponent, PropType, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import Avatar from './Avatar.vue';

import { local, store } from '@/store';
import { formatName } from '@/utils/strings';
import { UserProfile } from '@/utils/userprofile';

const EditProfile = defineAsyncComponent(() => import('./EditProfile.vue'));

defineProps({
    user: {
        type: UserProfile,
        default: () => new UserProfile(),
    },
    direction: {
        type: String as PropType<'horizontal' | 'vertical'>,
        default: 'vertical',
    },
});

const isEditing = ref(false);

const i18nMessages = {
    'zh-cn': { local: {
        anonymous: '匿名',
        editButton: '编辑信息',
    } },
    'en': { local: {
        anonymous: 'Anonymous',
        editButton: 'Edit Profile',
    } },
};

const { t } = useI18n({ messages: i18nMessages });

</script>

<style scoped lang="less">
/* 横向布局：窄屏顶部栏 */
.horizontal-profile {
    display: flex;
    flex-wrap: wrap;
    row-gap: 0.5rem;
    align-items: center;
    justify-content: space-between;
    background-color: var(--el-bg-color);
    border-bottom: 1px solid var(--el-border-color-light);
    box-sizing: border-box;

    .profile {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-shrink: 0;
    }

    .avatar {
        height: 64px;
        aspect-ratio: 1 / 1;
        overflow: hidden;
        flex-shrink: 0;
    }

    .username {
        font-weight: 600;
        font-size: var(--el-font-size-extra-large);
        color: var(--el-text-color-primary);
    }

    .id {
        font-size: var(--el-font-size-large);
        color: var(--el-text-color-secondary);
    }

    .realname {
        font-weight: 500;
        font-size: var(--el-font-size-large);
        color: var(--el-text-color-primary);
    }
    .fullname {
        font-size: var(--el-font-size-small);
        color: var(--el-text-color-regular);
    }

    .signature {
        width: 100%;
        max-height: 64px;
        overflow: auto;
        font-size: var(--el-font-size-extra-small);
        color: var(--el-text-color-placeholder);
        padding-left: 12px;
        white-space: pre-wrap;
    }

    .edit-button {
        margin-left: auto;
    }
}

/* 纵向布局：宽屏侧边栏 */
.vertical-profile {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    height: 100%;
    padding: 12px 8px;
    background-color: var(--el-bg-color);
    border-right: 1px solid var(--el-border-color-light);
    box-sizing: border-box;

    .profile {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
        margin-bottom: 16px;
    }

    .avatar {
        width: 100%;
        aspect-ratio: 1 / 1;
        overflow: hidden;
        margin-bottom: 8px;
    }

    .username {
        font-size: 18px;
        font-weight: 600;
        color: var(--el-text-color-primary);
        text-align: center;
    }

    .id {
        font-size: 13px;
        color: var(--el-text-color-secondary);
        text-align: center;
    }

    .realname {
        font-weight: 500;
        font-size: var(--el-font-size-large);
        color: var(--el-text-color-regular);
        text-align: center;
    }
    .fullname {
        font-size: var(--el-font-size-small);
        color: var(--el-text-color-regular);
        text-align: center;
    }

    .signature {
        width: 100%;
        font-size: var(--el-font-size-extra-small);
        line-height: 1.6;
        color: var(--el-text-color-placeholder);
        overflow: auto;
        word-break: break-word;
        white-space: pre-wrap;
    }

    .edit-button {
        width: 100%;
        margin-top: 1rem;
        order: 1;
    }
}
</style>

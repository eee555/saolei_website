<template>
    <span v-if="isUserAnonymous" class="text text-large">
        {{ t('common.msg.realNameRequired') }}
    </span>
    <div v-else>
        <div class="text text-large" style="padding: 0.1em; color: inherit;">
            {{ t('local.dragOrClick') }}
        </div>
        <el-checkbox v-model="local.autoUploadAfterParse" @click.stop>
            {{ t('local.autoUploadAfterParse') }}
        </el-checkbox>
        <el-checkbox v-model="local.autoRemoveAfterUpload" @click.stop>
            {{ t('local.autoRemoveAfterUpload') }}
        </el-checkbox>
        <div class="text text-small" style="padding: 0.1em;">
            {{ t('local.constraintSize') }}
        </div>
    </div>
</template>

<script setup lang="ts">
import { ElCheckbox } from 'element-plus';
import { useI18n } from 'vue-i18n';

import { local } from '@/store';

defineProps({
    isUserAnonymous: { type: Boolean, default: true },
});

/* 本地化 Localization */
const i18nMessages = {
    'zh-cn': { local: {
        dragOrClick: '将录像拉到此处或点击此处选择',
        autoUploadAfterParse: '解析完成自动上传',
        autoRemoveAfterUpload: '上传完成自动移除',
        constraintSize: '*单个文件大小不能超过5MB',
    } },
    'en': { local: {
        dragOrClick: 'Drag files here or click here to select',
        autoUploadAfterParse: 'Auto-upload after parsing',
        autoRemoveAfterUpload: 'Auto-remove after uploading',
        constraintSize: '*File size maximum is 5MB.',
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>

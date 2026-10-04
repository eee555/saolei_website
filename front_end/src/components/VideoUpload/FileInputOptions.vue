<template>
    <div class="file-input-options">
        <ElCheckbox v-model="local.autoUploadAfterParse" @click.stop>
            {{ t('local.autoUploadAfterParse') }}
        </ElCheckbox>
        <ElCheckbox v-model="local.autoRemoveAfterUpload" @click.stop>
            {{ t('local.autoRemoveAfterUpload') }}
        </ElCheckbox>
    </div>
</template>

<script setup lang="ts">
import { ElCheckbox } from 'element-plus';
import { useI18n } from 'vue-i18n';

import { local } from '@/store';

/* 本地化 Localization */
const i18nMessages = {
    'zh-cn': { local: {
        autoUploadAfterParse: '解析完成自动上传',
        autoRemoveAfterUpload: '上传完成自动移除',
    } },
    en: { local: {
        autoUploadAfterParse: 'Auto-upload after parsing',
        autoRemoveAfterUpload: 'Auto-remove after uploading',
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>

<style scoped>
.file-input-options {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0 8px;
    cursor: default;
}

.file-input-options .el-checkbox {
    margin: 0;
}
</style>

<template>
    <el-button style="height: 100%; align-items: center;" plain @click="formvisible = true">
        <base-icon-add />
    </el-button>

    <el-dialog
        v-model="formvisible" :title="t('accountlink.addLink')" width="25rem"
        @closed="form.platform = ''; form.identifier = '';"
    >
        <el-form :model="form">
            <el-form-item :label="t('accountlink.platform')">
                <el-select v-model="form.platform">
                    <el-option
                        v-for="(item, key) of platformlist" :key="key" :value="key" :label="item.name"
                        :disabled="userHasPlatform(key)"
                    />
                </el-select>
            </el-form-item>
            <el-form-item label="ID">
                <el-input v-model="form.identifier" maxlength="128" />
            </el-form-item>
            <el-form-item v-if="local.tooltip_show">
                <AccountLinkGuide :platform="form.platform" />
            </el-form-item>
            <el-form-item>
                <base-button-confirm :disabled="!formValid" @click.prevent="$emit('addLink', form.platform, form.identifier); formvisible=false" />
                <base-button-cancel @click.prevent="formvisible = false" />
            </el-form-item>
        </el-form>
    </el-dialog>
</template>

<script setup lang="ts">
import { ElButton, ElDialog, ElForm, ElFormItem, ElInput, ElOption, ElSelect } from 'element-plus';
import { computed, reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import { AccountLink } from './utils';

import BaseButtonCancel from '@/components/common/BaseButtonCancel.vue';
import BaseButtonConfirm from '@/components/common/BaseButtonConfirm.vue';
import { BaseIconAdd } from '@/components/common/icon';
import AccountLinkGuide from '@/components/dialogs/AccountLinkGuide.vue';
import { local } from '@/store';
import { platformlist } from '@/utils/common/accountLinkPlatforms';

const { t } = useI18n();

const props = defineProps({
    accountlinks: {
        type: Array<AccountLink>,
        default: () => [],
    },
});

const formvisible = ref(false);
const form = reactive({
    platform: '',
    identifier: '',
});

const formValid = computed(() => {
    switch (form.platform) {
        case 'a':
        case 'c':
        case 'q':
        case 'w': {
            const num = parseInt(form.identifier, 10);
            return !isNaN(num) && num.toString() === form.identifier && num > 0;
        }
        default:
            return false;
    }
});

function userHasPlatform(platform: string) {
    for (const item of props.accountlinks) {
        if (item.platform == platform) return true;
    }
    return false;
}

defineEmits<{
    (e: 'addLink', platform: string, identifier: string): void;
}>();

</script>

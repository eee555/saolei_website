<template>
    <div class="flex gap-2">
    <el-tag v-for="identifier of identifiers" closable @close="delIdentifier(identifier)">{{ identifier }}</el-tag>
    <el-input size="small" style="width: 200px" v-model="new_identifiers"></el-input>
    <el-link :underline="false" @click="addIdentifier(new_identifiers)"><el-icon><Plus/></el-icon></el-link>
</div>
</template>

<script setup lang="ts">

import { useUserStore } from '@/store';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { onMounted, ref } from 'vue';
import { removeItem } from '@/utils/system/tools';
import { Plus } from '@element-plus/icons-vue';
import { ElNotification } from 'element-plus';
import { generalNotification, unknownErrorNotification } from '@/utils/system/status';
import { useI18n } from 'vue-i18n';

const { proxy } = useCurrentInstance();
const store = useUserStore();
const identifiers = ref<string[]>([]);
const new_identifiers = ref("")
const t = useI18n();

onMounted(() => {
    proxy.$axios.get('msuser/identifiers/',
        {
            params: {
                id: store.user.id
            }
        }
    ).then(function (response) {
        identifiers.value = response.data;
    })
})

function delIdentifier(identifier: string) {
    proxy.$axios.post('identifier/del/',
        {
            identifier: identifier
        }
    ).then(function (response) {
        identifiers.value = removeItem(identifiers.value, identifier);
        ElNotification({
            title: t.t('identifierManager.delIdentifierSuccess'),
            message: t.t('identifierManager.processedNVideos', [response.data.value]),
            type: 'success'
        })
    }).catch(error => {
        generalNotification(t, error.response.status, t.t('common.action.addIdentifier'))
    })
}

function addIdentifier(identifier: string) {
    proxy.$axios.post('identifier/add/',
        {
            identifier: identifier,
        }
    ).then(function (response) {
        if (response.data.type === 'success') {
            identifiers.value.push(new_identifiers.value);
            ElNotification({
                title: t.t('identifierManager.addIdentifierSuccess'),
                message: t.t('identifierManager.processedNVideos', [response.data.value]),
                type: 'success'
            })
            store.new_identifier = false;
        } else if (response.data.category === 'notFound') {
            ElNotification({
                title: t.t('identifierManager.notFound'),
                type: 'error',
            })
        } else if (response.data.category === 'conflict') {
            ElNotification({
                title: t.t('identifierManager.conflict'),
                message: t.t('identifierManager.ownedBy', [response.data.value]),
                type: 'error',
            })
        } else {
            unknownErrorNotification(t)
        }
        new_identifiers.value = "";
    }).catch(error => {
        generalNotification(t, error.response.status, t.t('common.action.addIdentifier'))
    })
}

</script>

<template>
    <div class="flex gap-2">
    <el-tag v-for="designator of designators" closable @close="delDesignator(designator)">{{ designator }}</el-tag>
    <el-input size="small" style="width: 200px" v-model="new_designator"></el-input>
    <el-link :underline="false" @click="addDesignator(new_designator)"><el-icon><Plus/></el-icon></el-link>
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
const designators = ref<string[]>([]);
const new_designator = ref("")
const t = useI18n();

onMounted(() => {
    proxy.$axios.get('msuser/designators/',
        {
            params: {
                id: store.user.id
            }
        }
    ).then(function (response) {
        designators.value = response.data;
    })
})

function delDesignator(designator: string) {
    proxy.$axios.post('designator/del/',
        {
            designator: designator
        }
    ).then(function (response) {
        designators.value = removeItem(designators.value, designator);
        ElNotification({
            title: t.t('designatorManager.delDesignatorSuccess'),
            message: t.t('designatorManager.processedNVideos', [response.data.value]),
            type: 'success'
        })
    }).catch(error => {
        generalNotification(t, error.response.status, t.t('common.action.addDesignator'))
    })
}

function addDesignator(designator: string) {
    console.log(designator)
    proxy.$axios.post('designator/add/',
        {
            designator: designator,
        }
    ).then(function (response) {
        if (response.data.type === 'success') {
            designators.value.push(new_designator.value);
            ElNotification({
                title: t.t('designatorManager.addDesignatorSuccess'),
                message: t.t('designatorManager.processedNVideos', [response.data.value]),
                type: 'success'
            })
        } else if (response.data.category === 'notFound') {
            ElNotification({
                title: t.t('designatorManager.notFound'),
                type: 'error',
            })
        } else if (response.data.category === 'conflict') {
            ElNotification({
                title: t.t('designatorManager.conflict'),
                message: t.t('designatorManager.ownedBy', [response.data.value]),
                type: 'error',
            })
        } else {
            unknownErrorNotification(t)
        }
        new_designator.value = "";
    }).catch(error => {
        generalNotification(t, error.response.status, t.t('common.action.addDesignator'))
    })
}

</script>
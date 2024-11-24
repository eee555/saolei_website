<template>
    <div class="flex gap-2">
        <el-table :data="identifierdata">
            <el-table-column prop="data" sortable>
                <template #default="scope">
                    <el-input v-if="scope.row.data === ''" size="small" style="width: 200px"
                        v-model="new_identifiers"></el-input>
                </template>
            </el-table-column>
            <el-table-column>
                <template #default="scope">
                    <el-link v-if="scope.row.data === ''" :underline="false"
                        @click="addIdentifier(new_identifiers)"><el-icon>
                            <Plus />
                        </el-icon></el-link>
                    <el-link v-else :underline="false" @click="copyToClipboard(scope.row.data)">
                        <el-icon>
                            <CopyDocument />
                        </el-icon>
                    </el-link>
                    &nbsp;
                    <el-link v-if="store.player.id == store.user.id && scope.row.data !== ''" :underline="false" type="danger"
                        @click="delIdentifier(scope.row.data)">
                        <el-icon>
                            <Delete />
                        </el-icon>
                    </el-link>
                </template>
            </el-table-column>
        </el-table>
    </div>
</template>

<script setup lang="ts">

import { store } from '@/store';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { ref } from 'vue';
import { removeItem } from '@/utils/system/tools';
import { Plus } from '@element-plus/icons-vue';
import { ElNotification } from 'element-plus';
import { httpErrorNotification, unknownErrorNotification } from '@/components/Notifications';
import { useI18n } from 'vue-i18n';
import { computed } from 'vue';
import { copyToClipboard } from './CopyToClipboard';

const { proxy } = useCurrentInstance();
const new_identifiers = ref("")
const t = useI18n();

const identifierdata = computed(() => {
    let data = store.player.identifiers ? store.player.identifiers.map(value => ({ data: value })) : [];
    if (store.player.id == store.user.id) data.push({ data: "" });
    return data
})

function delIdentifier(identifier: string) {
    proxy.$axios.post('identifier/del/',
        {
            identifier: identifier
        }
    ).then(function (response) {
        store.player.identifiers = removeItem(store.player.identifiers, identifier);
        ElNotification({
            title: t.t('identifierManager.delIdentifierSuccess'),
            message: t.t('identifierManager.processedNVideos', [response.data.value]),
            type: 'success'
        })
    }).catch(httpErrorNotification)
}

function addIdentifier(identifier: string) {
    proxy.$axios.post('identifier/add/',
        {
            identifier: identifier,
        }
    ).then(function (response) {
        if (response.data.type === 'success') {
            store.player.identifiers.push(new_identifiers.value);
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
            unknownErrorNotification(response.data)
        }
        new_identifiers.value = "";
    }).catch(httpErrorNotification)
}

</script>

<style lang="less" scoped>
::v-deep(.el-table .el-table__cell) {
    font-family: 'Courier New', Courier, monospace;
    padding: 0;
    margin: 0;
}
</style>
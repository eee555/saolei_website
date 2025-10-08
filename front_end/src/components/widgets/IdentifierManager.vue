<template>
    <!-- 标识管理UI -->
    <!-- 表格第一列显示标识，用等宽字体。最后一行用来输入新的标识。第二列放操作按钮 -->
    <div class="flex gap-2">
        <el-table :data="identifierdata">
            <!-- 标识列 -->
            <el-table-column prop="data" sortable>
                <template #header>
                    <el-link v-if="store.player.id == store.user.id" :underline="false" @click="refreshIdentifiers">
                        <base-icon-refresh />
                    </el-link>
                </template>
                <template #default="scope">
                    <!-- 左margin是为了补偿输入框内文本的偏移 -->
                    <el-input
                        v-if="scope.row.data === ''" v-model="new_identifiers" size="small" style="width: 200px;margin-left: -7px"
                        input-style="font-family: 'Courier New', Courier, monospace;"
                    />
                </template>
            </el-table-column>
            <!-- 操作列 -->
            <el-table-column>
                <template #default="scope">
                    <!-- 添加标识 -->
                    <el-link
                        v-if="scope.row.data === ''" :underline="false"
                        @click="addIdentifier(new_identifiers)"
                    >
                        <base-icon-add />
                    </el-link>
                    <!-- 复制标识 -->
                    <IconCopy v-else :text="scope.row.data" />
                    &nbsp;
                    <!-- 删除标识 -->
                    <el-link
                        v-if="store.player.id == store.user.id && scope.row.data !== ''" :underline="false"
                        type="danger" @click="delIdentifier(scope.row.data)"
                    >
                        <base-icon-delete />
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
import { ElNotification, ElTable, ElTableColumn, ElLink, ElInput } from 'element-plus';
import { httpErrorNotification, unknownErrorNotification } from '@/components/Notifications';
import { useI18n } from 'vue-i18n';
import { computed } from 'vue';
import BaseIconDelete from '@/components/common/BaseIconDelete.vue';
import IconCopy from './IconCopy.vue';
import BaseIconAdd from '@/components/common/BaseIconAdd.vue';
import BaseIconRefresh from '@/components/common/BaseIconRefresh.vue';

const { proxy } = useCurrentInstance();
const new_identifiers = ref('');
const { t } = useI18n();

const identifierdata = computed(() => {
    const data = store.player.identifiers ? store.player.identifiers.map((value) => ({ data: value })) : [];
    if (store.player.id == store.user.id) data.push({ data: '' });
    return data;
});

function delIdentifier(identifier: string) {
    proxy.$axios.post('identifier/del/', { identifier: identifier },
    ).then(function (response) {
        store.player.identifiers = removeItem(store.player.identifiers, identifier);
        ElNotification({
            title: t('identifierManager.delIdentifierSuccess'),
            message: t('identifierManager.processedNVideos', [response.data.value]),
            type: 'success',
        });
    }).catch(httpErrorNotification);
}

function addIdentifier(identifier: string) {
    proxy.$axios.post('identifier/add/', { identifier: identifier },
    ).then(function (response) {
        if (response.data.type === 'success') {
            store.player.identifiers.push(new_identifiers.value);
            ElNotification({
                title: t('identifierManager.addIdentifierSuccess'),
                message: t('identifierManager.processedNVideos', [response.data.value]),
                type: 'success',
            });
            store.new_identifier = false;
        } else if (response.data.category === 'notFound') {
            ElNotification({
                title: t('identifierManager.notFound'),
                type: 'error',
            });
        } else if (response.data.category === 'conflict') {
            ElNotification({
                title: t('identifierManager.conflict'),
                message: t('identifierManager.ownedBy', [response.data.value]),
                type: 'error',
            });
        } else {
            unknownErrorNotification(response.data);
        }
        new_identifiers.value = '';
    }).catch(httpErrorNotification);
}

function refreshIdentifiers() {
    proxy.$axios.post('identifier/refresh/').then((response) => {
        store.player.identifiers = response.data;
    }).catch(httpErrorNotification);
}

</script>

<style lang="less" scoped>
::v-deep(.el-table .el-table__cell) {
    font-family: 'Courier New', Courier, monospace;
    font-size: 12px;
    padding: 0;
    margin: 0;
}
</style>

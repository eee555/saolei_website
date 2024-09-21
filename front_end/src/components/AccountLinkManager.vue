<template>
    <el-table :data="accountlinks">
        <el-table-column prop="platform" label="平台" />
        <el-table-column prop="identifier" label="ID" />
        <el-table-column prop="verified" label="状态" />
        <el-table-column label="操作">
            <template #default="scope">
                <el-link :underline="false" @click.prevent="deleteRow(scope.$index)">删除</el-link>
            </template>
        </el-table-column>
    </el-table>
    <el-button style="width:100%" @click="formvisible = true">
        <el-icon>
            <Plus />
        </el-icon>
    </el-button>
    <el-dialog v-model="formvisible" title="添加关联账号" @closed="form.platform = ''; form.identifier = '';" width="500px">
        <el-form :model="form">
            <el-form-item label="平台">
                <el-select v-model="form.platform">
                    <el-option v-for="item in platformlist" :value="item.key" :label="item.name" />
                </el-select>
            </el-form-item>
            <el-form-item label="ID">
                <el-input v-model="form.identifier" maxlength="128" />
            </el-form-item>
            <el-form-item>
                <el-button type="primary" :disabled="!formValid" @click.prevent="addLink(); formvisible=false;">确认</el-button>
                <el-button @click.prevent="formvisible=false">取消</el-button>
            </el-form-item>
        </el-form>
    </el-dialog>
</template>

<script setup lang="ts">

import { computed, onMounted, reactive, ref } from 'vue';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { useUserStore } from '@/store';
import { Action, ElMessageBox } from 'element-plus';

interface AccountLink {
    platform: string;
    identifier: string;
    verified: boolean;
}

const { proxy } = useCurrentInstance();
const store = useUserStore();
const accountlinks = ref<AccountLink[]>([]);
const formvisible = ref(false);
const form = reactive({
    platform: '',
    identifier: '',
})
const platformlist = [
    { key: 'c', name: '扫雷网', },
]

const refresh = () => {
    proxy.$axios.get('accountlink/get/',
        {
            params: {
                id: store.user.id
            }
        }
    ).then(function (response) {
        accountlinks.value = response.data;
    })
}
onMounted(refresh)

const formValid = computed(() => {
    switch (form.platform) {
        case 'c':
            const num = parseInt(form.identifier, 10);
            return !isNaN(num) && num.toString() === form.identifier && num > 0
        default:
            return false;
    }
})

const addLink = () => {
    proxy.$axios.post('accountlink/add/',
        {
            platform: form.platform,
            identifier: form.identifier,
        }
    ).then(function (response) {
        refresh()
    })
}

const deleteRow = (index: number) => {
    ElMessageBox.confirm(accountlinks.value[index], '确认删除以下账号关联吗？').then(() => {
        proxy.$axios.post('accountlink/delete/', {platform: accountlinks.value[index].platform}).then(function (response) {
            refresh()
        })
    }).catch(() => {})
}

</script>
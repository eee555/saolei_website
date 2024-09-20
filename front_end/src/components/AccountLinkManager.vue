<template>
    <el-table :data="accountlinks">
        <el-table-column prop="platform" label="平台" />
        <el-table-column prop="identifier" label="ID" />
        <el-table-column prop="verified" label="状态" />
    </el-table>
    <el-button style="width:100%" @click="formvisible = true">
        <el-icon>
            <Plus />
        </el-icon>
    </el-button>
    <el-dialog v-model="formvisible" title="添加关联账号" style="width:600px">
        <el-input v-model="form.identifier" size="small" maxlength="128" style="width:100%">
            <template #prepend>
                <el-select v-model="form.platform" size="small" style="width:330px">
                    <el-option v-for="item in platformlist" :value="item.key" :label="item.url" />
                </el-select>
            </template>
        </el-input>
    </el-dialog>
</template>

<script setup lang="ts">

import { onMounted, reactive, ref } from 'vue';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { useUserStore } from '@/store';

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
    { key: 'a', url: 'https://minesweepergame.com/profile.php?pid=', },
    { key: 'w', url: 'https://minesweeper.online/player/', },
    { key: 'c', url: 'http://saolei.wang/Player/Index.asp?Id=', },
    { key: 'B', url: 'https://space.bilibili.com/', },
    { key: 'G', url: 'https://github.com/', },
]

onMounted(() => {
    proxy.$axios.get('accountlink/get/',
        {
            params: {
                id: store.user.id
            }
        }
    ).then(function (response) {
        accountlinks.value = response.data;
    })
})

</script>
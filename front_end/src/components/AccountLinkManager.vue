<template>
    <el-table :data="accountlinks">
        <el-table-column prop="platform" label="平台" />
        <el-table-column prop="identifier" label="ID" />
        <el-table-column prop="verified" label="状态" />
    </el-table>
</template>

<script setup lang="ts">

import { onMounted, ref } from 'vue';
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
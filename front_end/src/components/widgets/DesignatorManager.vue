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

const { proxy } = useCurrentInstance();
const store = useUserStore();
const designators = ref<String[]>([]);
const new_designator = ref("")

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
    })
}

function addDesignator(designator: string) {
    console.log(designator)
    proxy.$axios.post('designator/add/',
        {
            designator: designator,
        }
    ).then(function (response) {
        designators.value.push(new_designator.value);
        new_designator.value = "";
    })
}

</script>
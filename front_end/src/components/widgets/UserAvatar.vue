<template>
    <el-image :src="`${proxy.$axios.defaults.baseURL}/api/userprofile/avatar/${userId}`" style="max-height: 100%; max-width: 100%; aspect-ratio: 1 / 1;">
        <template #error>
            <img src="@/assets/person.png" style="max-height: 100%; max-width: 100%; aspect-ratio: 1 / 1;">
        </template>
    </el-image>
</template>

<script setup lang="ts">
import useCurrentInstance from '@/utils/common/useCurrentInstance';

defineProps({
    userId: { type: Number, required: true },
});

const { proxy } = useCurrentInstance();

</script>

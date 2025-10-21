<template>
    <el-tooltip v-if="local.menu_icon" :content="props.text">
        <el-icon class="menumargin">
            <slot v-if="props.usehtml" />
            <component :is="props.icon" v-else class="menuicon" />
        </el-icon>
    </el-tooltip>
    <span v-else style="padding-right: 5px">
        <el-icon>
            <slot v-if="props.usehtml" />
            <component :is="props.icon" v-else class="menuicon" />
        </el-icon>{{ props.text }}
    </span>
</template>

<script lang="ts" setup>
import { ElIcon, ElTooltip } from 'element-plus';

import { local } from '@/store';

const props = defineProps({
    text: { type: String, required: true },
    icon: { type: String, required: true },
    usehtml: {
        type: Boolean,
        default: false,
    },
});

</script>

<style lang="less" scoped>
.menuicon {
    width: 60px;
    height: 60px;
}

.menumargin {
    margin-top: 0px;
    margin-bottom: 0px;
}
</style>

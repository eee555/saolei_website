<template>
    <el-tooltip v-if="local.menu_icon" :content="props.text">
        <el-icon class="menumargin">
            <slot v-if="props.usehtml" />
            <component v-else :is="props.icon" class="menuicon" />
        </el-icon>
    </el-tooltip>
    <span v-else style="padding-right: 5px">
        <el-icon>
            <slot v-if="props.usehtml" />
            <component v-else :is="props.icon" class="menuicon" />
        </el-icon>{{ props.text }}
    </span>
</template>

<script lang="ts" setup>

import { local } from "@/store";

const props = defineProps({
    text: String,
    icon: String,
    usehtml: {
        type: Boolean,
        default: false,
    },
})

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
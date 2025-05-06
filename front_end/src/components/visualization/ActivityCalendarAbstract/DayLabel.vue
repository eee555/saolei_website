<template>
    <el-text
        :style="{
            display: 'inline-block',
            fontSize: `${cellFullSize - 8}px`,
            lineHeight: `${cellFullSize}px`,
            marginTop: '0',
            marginRight: `${cellMargin}px`,
        }"
    >
        <IconSetting>
            <Setting />
        </IconSetting><br>
        Sun<br>Mon<br>Tue<br>Wed<br>Thu<br>Fri<br>Sat
    </el-text>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { ElText } from 'element-plus';
import IconSetting from '@/components/widgets/IconSetting.vue';
import Setting from './Setting.vue';

const prop = defineProps({
    cellSize: { type: Number, default: 14 }, // 格子大小，单位为px
    cellMargin: { type: Number, default: 3 }, // 格子间距，单位为px
});

const cellFullSize = computed(() => prop.cellSize + prop.cellMargin);

</script>

<template>
    <Tippy v-if="video" :style="cellStyle" :duration="0" sticky>
        <ElLink underline="never" @click="preview(video.id, video.software)">
            {{ text }}
        </ElLink>
        <template #content>
            <ElCard class="card-small">
                <VideoAbstractDisplay :video="video" />
            </ElCard>
        </template>
    </Tippy>
    <span v-else :style="cellStyle">
        {{ text }}
    </span>
</template>

<script setup lang="ts">
import '@/styles/text.css';
import '@/styles/cards.css';

import { ElCard, ElLink } from 'element-plus';
import type { PropType } from 'vue';
import { computed } from 'vue';
import { Tippy } from 'vue-tippy';

import VideoAbstractDisplay from '@/components/widgets/VideoAbstractDisplay.vue';
import { PiecewiseColorScheme } from '@/utils/colors';
import { preview } from '@/utils/common/PlayerDialog';
import type { VideoAbstract } from '@/utils/videoabstract';

const props = defineProps({
    video: { type: Object as PropType<VideoAbstract | undefined>, default: undefined },
    text: { type: String, default: '' },
    value: { type: Number, default: NaN },
    colorTheme: { type: Object as PropType<PiecewiseColorScheme>, default: new PiecewiseColorScheme([], []) },
});

const cellStyle = computed(() => props.colorTheme.getStyle(props.value));
</script>

<style lang="less" scoped>
.el-link {
    --el-link-text-color: currentColor;
}
</style>

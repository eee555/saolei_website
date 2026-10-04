<template>
    <Tippy v-if="video" :style="cellStyle" :duration="0" sticky>
        <BaseTextButton class="video-cell-action" data-cy="video-cell-action" @click="preview(video.id, video.software)">
            {{ text }}
        </BaseTextButton>
        <template #content>
            <div class="card card-small">
                <VideoAbstractDisplay :video="video" />
            </div>
        </template>
    </Tippy>
    <span v-else :style="cellStyle">
        {{ text }}
    </span>
</template>

<script setup lang="ts">
import '@/styles/text.css';
import '@/styles/cards.css';

import type { PropType } from 'vue';
import { computed } from 'vue';
import { Tippy } from 'vue-tippy';

import BaseTextButton from '@/components/common/BaseTextButton.vue';
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
.video-cell-action {
    --button-accent: currentColor;
}
</style>

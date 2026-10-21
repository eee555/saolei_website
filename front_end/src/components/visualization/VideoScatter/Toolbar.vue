<template>
    <div class="video-scatter-toolbar">
        <div style="display: flex; gap: 1em; justify-content: flex-end; align-items: center">
            <!-- 选择xy用的数据 -->
            <div style="width: 24em; display: flex; gap: 1em;">
                <MSStatSelect v-model="VideoScatterConfig.x" label="x" :options="[...VideoScatterAxisChoice]" :append-to="isFullscreen ? '.video-scatter' : undefined" :popper-options="popperOptions" />
                <MSStatSelect v-model="VideoScatterConfig.y" label="y" :options="[...VideoScatterAxisChoice]" :append-to="isFullscreen ? '.video-scatter' : undefined" :popper-options="popperOptions" />
                <MSStatSelect v-model="VideoScatterConfig.colorBy" :label="t('local.colorBy')" :options="[...VideoScatterColorByChoice]" :append-to="isFullscreen ? '.video-scatter' : undefined" :popper-options="popperOptions" />
            </div>

            <div style="flex-grow: 1" />

            <!-- 设置散点的属性 -->
            <div>
                <MarkerSetting
                    v-model:radius="VideoScatterConfig.radius"
                    options="radius"
                />
            </div>

            <ElSegmented
                v-model="VideoScatterStore.canvasMode"
                :options="[
                    {
                        label: t('local.cursor'),
                        value: '',
                    },
                    {
                        label: t('local.select'),
                        value: 'select',
                    },
                ]"
            />

            <div class="button-group">
                <BaseButton
                    class="square-button"
                    type="primary" :plain="!isFullscreen"
                    :title="t('local.fullscreen')"
                    :aria-label="t('local.fullscreen')" :aria-pressed="isFullscreen"
                    @click="emit('toggleFullscreen')"
                >
                    <i class="pi pi-expand" />
                </BaseButton>
                <BaseButton
                    type="primary"
                    :plain="!VideoScatterConfig.showOnlySelected"
                    :title="t('local.hideNonSelected')"
                    :aria-label="t('local.hideNonSelected')" :aria-pressed="VideoScatterConfig.showOnlySelected"
                    class="square-button"
                    @click="VideoScatterConfig.showOnlySelected = !VideoScatterConfig.showOnlySelected"
                >
                    <BaseIconHide />
                </BaseButton>
                <BaseButton
                    type="primary"
                    :plain="!VideoScatterConfig.highlightSelected"
                    :title="t('local.highlightSelected')"
                    :aria-label="t('local.highlightSelected')" :aria-pressed="VideoScatterConfig.highlightSelected"
                    class="square-button"
                    @click="VideoScatterConfig.highlightSelected = !VideoScatterConfig.highlightSelected"
                >
                    <i class="pi pi-star" />
                </BaseButton>
            </div>
        </div>
        <div class="selection-panel-secondary">
            <ElSegmented
                v-if="VideoScatterStore.canvasMode === 'select'"
                v-model="VideoScatterStore.selectionMode"
                :options="[
                    {
                        label: t('local.assign'),
                        value: 'assign',
                    },
                    {
                        label: t('local.union'),
                        value: 'union',
                    },
                    {
                        label: t('local.diff'),
                        value: 'diff',
                    },
                    {
                        label: t('local.intersect'),
                        value: 'intersect',
                    },
                ]"
            />
        </div>
    </div>
</template>

<script setup lang="ts">
import 'primeicons/primeicons.css';
import '@/styles/button.css';

import { ElSegmented } from 'element-plus';
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

import { VideoScatterStore } from './store';

import BaseButton from '@/components/common/BaseButton.vue';
import { BaseIconHide } from '@/components/common/icon';
import MSStatSelect from '@/components/Filters/MSStatSelect.vue';
import { MarkerSetting } from '@/components/visualization/Plots';
import { VideoScatterAxisChoice, VideoScatterColorByChoice, VideoScatterConfig } from '@/store';

const props = defineProps({
    isFullscreen: { type: Boolean, default: false },
});

const emit = defineEmits<{
    toggleFullscreen: [];
}>();

// 全屏时散点图根元素是 position: fixed，祖先卡片塌缩，Popper 会把这些祖先当作
// 裁剪边界，误判下方空间不足把下拉翻到右侧。这里改为以 viewport 为边界。
const popperOptions = computed(() => {
    if (!props.isFullscreen) return undefined;
    return {
        modifiers: [
            {
                name: 'flip',
                options: {
                    boundary: 'viewport',
                    fallbackPlacements: ['bottom-start', 'top-start'],
                },
            },
            { name: 'preventOverflow', options: { boundary: 'viewport' } },
        ],
    };
});

const i18nMessages = {
    'zh-cn': { local: {
        assign: '覆盖',
        select: '框选',
        colorBy: '颜色',
        cursor: '光标',
        diff: '差集',
        fullscreen: '全屏',
        hideNonSelected: '隐藏未选中项',
        highlightSelected: '高亮选中项',
        intersect: '交集',
        union: '并集',
    } },
    en: { local: {
        assign: 'New',
        select: 'Select points',
        colorBy: 'Color by',
        cursor: 'Cursor',
        diff: 'Difference',
        fullscreen: 'Fullscreen',
        hideNonSelected: 'Hide non-selected',
        highlightSelected: 'Highlight selected',
        intersect: 'Intersection',
        union: 'Union',
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>

<style lang="less" scoped>
.video-scatter-toolbar {
    display: flex;
    flex-direction: column;
    gap: 0.5em;
}

.selection-panel-secondary {
    align-items: center;
    display: flex;
    flex-wrap: wrap;
    gap: 0.75em;
}
</style>

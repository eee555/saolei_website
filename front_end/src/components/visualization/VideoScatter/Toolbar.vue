<template>
    <div class="video-scatter-toolbar">
        <div style="display: flex; gap: 1em; justify-content: flex-end; align-items: center">
            <!-- 选择xy用的数据 -->
            <div style="width: 14em; display: flex; gap: 1em;">
                <MSStatSelect v-model="VideoScatterConfig.x" label="x" :options="[...VideoScatterAxisChoice]" />
                <MSStatSelect v-model="VideoScatterConfig.y" label="y" :options="[...VideoScatterAxisChoice]" />
            </div>

            <div style="flex-grow: 1" />

            <!-- 设置散点的属性 -->
            <div>
                <MarkerSetting
                    v-model:radius="VideoScatterConfig.radius"
                    options="radius"
                />
            </div>

            <el-segmented
                v-model="VideoScatterStore.canvasMode"
                :options="[
                    {
                        label: '光标',
                        value: '',
                    },
                    {
                        label: '框选',
                        value: 'select',
                    },
                ]"
            />

            <div class="toggle-switches">
                <el-button
                    type="primary"
                    :plain="!VideoScatterConfig.showOnlySelected"
                    title="Hide non-selected"
                    style="padding: 8px"
                    @click="VideoScatterConfig.showOnlySelected = !VideoScatterConfig.showOnlySelected"
                >
                    <BaseIconHide />
                </el-button>
                <el-button
                    type="primary"
                    :plain="!VideoScatterConfig.highlightSelected"
                    title="Highlight selected"
                    style="padding: 8px; margin: 0"
                    @click="VideoScatterConfig.highlightSelected = !VideoScatterConfig.highlightSelected"
                >
                    <i class="pi pi-star" />
                </el-button>
            </div>
        </div>
        <div class="selection-panel-secondary">
            <el-segmented
                v-if="VideoScatterStore.canvasMode === 'select'"
                v-model="VideoScatterStore.selectionMode"
                :options="[
                    {
                        label: '覆盖',
                        value: 'assign',
                    },
                    {
                        label: '并集',
                        value: 'union',
                    },
                    {
                        label: '差集',
                        value: 'diff',
                    },
                    {
                        label: '交集',
                        value: 'intersect',
                    },
                ]"
            />
        </div>
    </div>
</template>

<script setup lang="ts">
import 'primeicons/primeicons.css';
import '@/styles/text.css';

import { ElButton, ElSegmented } from 'element-plus';

import { VideoScatterStore } from './store';

import { BaseIconHide } from '@/components/common/icon';
import MSStatSelect from '@/components/Filters/MSStatSelect.vue';
import { MarkerSetting } from '@/components/visualization/Plots';
import { VideoScatterAxisChoice, VideoScatterConfig } from '@/store';
</script>

<style lang="less" scoped>
.video-scatter-toolbar {
    display: flex;
    flex-direction: column;
    gap: 0.5em;
}

.selection-panel-primary {
    align-items: center;
    display: flex;
    flex-wrap: wrap;
    gap: 0.75em;
}

.selection-panel-secondary {
    align-items: center;
    display: flex;
    flex-wrap: wrap;
    gap: 0.75em;
}

.toggle-switches {
    display: flex;
    gap: 0.25em;
}
</style>

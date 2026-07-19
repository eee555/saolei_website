<template>
    <div class="custom-counter-config-editor">
        <div class="custom-counter-config-editor__toolbar">
            <ElCheckbox v-model="developerMode">
                Developer Mode
            </ElCheckbox>
        </div>

        <CustomCounterJsonEditor v-if="developerMode" v-model="config" />
        <CustomCounterRowsEditor v-else v-model="config" />
    </div>
</template>

<script setup lang="ts">
import { ElCheckbox } from 'element-plus';
import type { PropType } from 'vue';
import { ref } from 'vue';

import CustomCounterJsonEditor from './CustomCounterJsonEditor.vue';
import CustomCounterRowsEditor from './CustomCounterRowsEditor.vue';
import type { CustomCounterConfig } from './types';

const config = defineModel({
    type: Array as PropType<CustomCounterConfig>,
    required: true,
});

const developerMode = ref(false);
</script>

<style scoped>
.custom-counter-config-editor {
    display: flex;
    flex-direction: column;
    width: 40rem;
    min-width: min(100%, 40rem);
    max-height: calc(100vh - 290px);
    min-height: 0;
    overflow: hidden;
}

.custom-counter-config-editor__toolbar {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 12px;
    margin-bottom: 8px;
}
</style>

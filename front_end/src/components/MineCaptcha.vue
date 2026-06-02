<template>
    <div class="mine-captcha">
        <div class="hint">{{ t('form.openAllSafe') }}</div>
        <div v-if="loading" class="loading">{{ t('form.captchaLoading') }}</div>
        <div v-else-if="loadFailed" class="loading">{{ t('form.captchaLoadingFail') }}</div>
        <div v-else class="grid" :style="{ gridTemplateColumns: `repeat(${width}, 28px)` }">
            <!-- top row: numbers -->
            <div
                v-for="(n, i) in top" :key="`top-${i}`"
                class="cell revealed"
                :class="`num-${n}`"
            >
                {{ n }}
            </div>
            <!-- bottom row: clickable -->
            <div
                v-for="i in width" :key="`bot-${i - 1}`"
                class="cell"
                :class="opened.has(i - 1) ? 'revealed opened' : 'unrevealed'"
                :data-cy="`mine-cell-${i - 1}`"
                @click="toggleOpen(i - 1)"
            />
        </div>
        <button type="button" class="refresh-btn" @click="refreshPic">🔄</button>
    </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import { httpErrorNotification, unknownErrorNotification } from './Notifications';

import useCurrentInstance from '@/utils/common/useCurrentInstance';

const { proxy } = useCurrentInstance();
const { t } = useI18n();

const hashkey = ref('');
const top = ref<number[]>([]);
const width = ref(5);
const opened = ref<Set<number>>(new Set());
const loading = ref(true);
const loadFailed = ref(false);

const refreshPic = () => {
    loading.value = true;
    loadFailed.value = false;
    opened.value = new Set();
    proxy.$axios.get('/userprofile/refresh_captcha/').then((response) => {
        if (response.data.status === 100) {
            hashkey.value = response.data.hashkey;
            top.value = response.data.top;
            width.value = response.data.top.length;
        } else {
            unknownErrorNotification(response.data);
            loadFailed.value = true;
        }
        loading.value = false;
    }).catch((error) => {
        httpErrorNotification(error);
        loadFailed.value = true;
        loading.value = false;
    });
};

const toggleOpen = (idx: number) => {
    const next = new Set(opened.value);
    if (next.has(idx)) next.delete(idx);
    else next.add(idx);
    opened.value = next;
};

const getResponse = (): string => {
    return [...opened.value].sort((a, b) => a - b).join(',');
};

const openedCount = () => opened.value.size;

onMounted(refreshPic);

defineExpose({
    hashkey,
    refreshPic,
    getResponse,
    openedCount,
});
</script>

<style scoped>
.mine-captcha {
    display: inline-flex;
    flex-direction: column;
    gap: 4px;
    align-items: flex-start;
}
.hint {
    font-size: 12px;
    color: #606266;
}
.loading {
    height: 64px;
    line-height: 64px;
    color: #909399;
}
.grid {
    display: grid;
    grid-auto-rows: 28px;
    gap: 2px;
}
.cell {
    width: 28px;
    height: 28px;
    text-align: center;
    line-height: 28px;
    font-weight: bold;
    font-family: monospace;
    user-select: none;
}
.cell.revealed {
    background: #c0c0c0;
    border: 1px solid #808080;
}
.cell.unrevealed {
    background: #bdbdbd;
    border-top: 2px solid #ffffff;
    border-left: 2px solid #ffffff;
    border-right: 2px solid #7b7b7b;
    border-bottom: 2px solid #7b7b7b;
    cursor: pointer;
}
.cell.unrevealed:hover {
    background: #d4d4d4;
}
.cell.revealed.opened {
    background: #d4d4d4;
    cursor: pointer;
}
.num-1 { color: #0000ff; }
.num-2 { color: #008000; }
.num-3 { color: #ff0000; }
.num-4 { color: #000080; }
.num-5 { color: #800000; }
.num-6 { color: #008080; }
.refresh-btn {
    align-self: flex-end;
    background: none;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    cursor: pointer;
    padding: 2px 6px;
}
</style>

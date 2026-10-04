<template>
    <div
        class="base-file-input" :class="{ 'base-file-input--dragover': isDragover && !disabled, 'base-file-input--disabled': disabled }"
        @dragover.prevent="onDragOver"
        @dragleave.prevent="onDragLeave"
        @drop.prevent="onDrop"
        @click.self="triggerFileDialog"
    >
        <!-- 隐藏的原生 input：用于点击选择文件 -->
        <input ref="fileInputRef" type="file" multiple :accept="accept" :disabled="disabled" style="display: none" @change="onFileSelect">

        <button type="button" class="base-button base-file-input__trigger" :disabled="disabled" @click="triggerFileDialog">
            <slot name="default">
                <span>点击此处或拖拽文件到此区域</span>
            </slot>
        </button>
        <!-- 交互选项放在按钮外，避免在 button 中嵌套表单控件。 -->
        <div v-if="$slots.options" class="base-file-input__options">
            <slot name="options" />
        </div>
    </div>
</template>

<script setup lang="ts">
import '@/styles/button.css';
import { ref, useTemplateRef } from 'vue';

const props = defineProps({
    // 限制文件类型，例如 'image/*' 或 '.pdf,.jpg'
    accept: {
        type: String,
        default: '',
    },
    // 是否禁用组件
    disabled: {
        type: Boolean,
        default: false,
    },
});

const emit = defineEmits(['add']);

defineSlots<{
    default?: () => unknown;
    options?: () => unknown;
}>();

const fileInputRef = useTemplateRef('fileInputRef');
const isDragover = ref(false);

// 触发原生文件选择框
const triggerFileDialog = () => {
    if (props.disabled) return;
    fileInputRef.value?.click();
};

// 处理 input 的 change 事件（点击选择后）
function onFileSelect(event: Event) {
    const target = event.target as HTMLInputElement;
    const files = Array.from(target.files ?? []);
    // 清空 input，允许再次选择相同文件；禁用期间不接收选择结果。
    target.value = '';
    if (props.disabled) return;
    if (files.length) {
        emit('add', files);
    }
}

// 拖拽进入区域
function onDragOver() {
    if (props.disabled) return;
    isDragover.value = true;
}

// 拖拽离开区域
function onDragLeave() {
    isDragover.value = false;
}

// 放下文件
function onDrop(event: DragEvent) {
    isDragover.value = false;
    if (props.disabled) return;
    if (!event.dataTransfer) return;
    const files = Array.from(event.dataTransfer.files);
    if (files.length) {
        emit('add', files);
    }
}
</script>

<style scoped>
.base-file-input {
    display: flex;
    box-sizing: border-box;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100%;
    border: 1px solid var(--el-border-color);
    padding: 8px;
    background: var(--el-fill-color-blank);
    color: var(--el-text-color-regular);
    text-align: center;
    cursor: pointer;
}

.base-file-input__trigger {
    --button-color: inherit;
    --button-hover-color: inherit;
    --button-hover-background: transparent;
    --button-active-background: transparent;
    --button-disabled-background: transparent;

    flex-direction: column;
    width: 100%;
    border: 0;
    background: transparent;
}

.base-file-input__options {
    max-width: 100%;
    cursor: default;
}

.base-file-input:not(.base-file-input--disabled):hover:not(:has(.base-file-input__options:hover)) {
    border-color: var(--el-color-primary-light-7);
    background: var(--el-color-primary-light-9);
    color: var(--el-color-primary);
}

.base-file-input:not(.base-file-input--disabled):active:not(:has(.base-file-input__options:hover)) {
    background: var(--el-color-primary-light-8);
}

.base-file-input--dragover {
    border-color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
}

.base-file-input--disabled {
    border-color: var(--el-disabled-border-color);
    background: var(--el-disabled-bg-color);
    color: var(--el-disabled-text-color);
    cursor: not-allowed;
}
</style>

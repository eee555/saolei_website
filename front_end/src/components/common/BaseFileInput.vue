<template>
    <el-button
        style="width: 100%"
        size="large"
        @dragover.prevent="onDragOver"
        @dragleave.prevent="onDragLeave"
        @drop.prevent="onDrop"
        @click="triggerFileDialog()"
    >
        <!-- 隐藏的原生 input：用于点击选择文件 -->
        <input ref="fileInputRef" type="file" multiple :accept="accept" :disabled="disabled" style="display: none" @change="onFileSelect">

        <!-- 可自定义的默认区域 -->
        <slot name="default">
            <!-- 默认占位内容 -->
            <span>点击此处或拖拽文件到此区域</span>
        </slot>
    </el-button>
</template>

<script setup lang="ts">
import { ElButton } from 'element-plus';
import { ref } from 'vue';

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

const fileInputRef = ref<HTMLInputElement>();
const isDragover = ref(false);

// 触发原生文件选择框
const triggerFileDialog = () => {
    if (props.disabled) return;
    fileInputRef.value!.click();
};

// 处理 input 的 change 事件（点击选择后）
function onFileSelect(event: Event) {
    const target = event.target as HTMLInputElement;
    if (!target.files) return;
    const files = Array.from(target.files);
    if (files.length) {
        emit('add', files);
    }
    fileInputRef.value!.value = '';
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
    if (props.disabled) return;
    isDragover.value = false;
    if (!event.dataTransfer) return;
    const files = Array.from(event.dataTransfer.files);
    if (files.length) {
        emit('add', files);
    }
}

const emit = defineEmits(['add']);
</script>

<style scoped>
.base-file-input {
    border-radius: 8px;
    padding: 20px;
    text-align: center;
    transition: all 0.2s;
    cursor: pointer;
}

.default-content {
    user-select: none;
}

.sub-hint {
    font-size: 12px;
    margin-left: 8px;
}

.drag-hint {
    font-weight: bold;
}
</style>

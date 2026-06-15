<template>
    <iframe
        ref="iframeRef" :width="iframeWidth" :height="iframeHeight"
        src="/flop/index.html" style="border: none"
        @load="onIframeLoad"
    />
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';

import { videoplayerstore } from '@/store';

declare global {
    interface FlopPlayer {
        playVideo: (src: string, options: any) => void;
    }

    interface FlopPlaceholder {
        onload: () => void;
    }

    interface Window {
        flop: FlopPlayer | FlopPlaceholder | null;
    }
}

const props = defineProps({
    src: { type: String, default: '' },
});

watch(() => props.src, () => {
    if (props.src === '') return;
    window.flop = {
        onload: async function () {
            playVideo();
        },
    };
}, { immediate: true });

function playVideo() {
    (window.flop as FlopPlayer).playVideo(props.src, {
        share: {
            uri: props.src,
            pathname: '/flop-player/player',
            anonymous: false,
            background: 'rgba(0, 0, 0, 0)',
            title: 'Flop Player Share',
            favicon: 'https://avatars.githubusercontent.com/u/38378650?s=32', // 胡帝的头像
        },
        anonymous: false,
        background: 'rgba(0, 0, 0, 0)',
        listener: function () {
            videoplayerstore.visible = false;
            window.flop = null;
        },
    });
}

const iframeRef = ref<HTMLIFrameElement | null>(null);
const iframeWidth = ref(0);
const iframeHeight = ref(0);
const backgroundColor = computed(() => getComputedStyle(document.documentElement).getPropertyValue('--el-bg-color'));

onMounted(() => {
    iframeRef.value!.onload = function () {
        // 获取 iframe 内部的 document 对象
        const iframeDoc = iframeRef.value!.contentDocument || iframeRef.value!.contentWindow!.document;
        // 修改 body 背景色
        // iframeDoc.body.style.backgroundColor = '#000000';
        // 或者添加一个全局样式
        iframeDoc.body.style.background = '#000000';
    };
});

let resizeObserver: ResizeObserver | null = null;
let mutationObserver: MutationObserver | null = null;

// 获取内部真实内容尺寸（不受 iframe 当前宽高限制）
const getContentSize = (iframe: HTMLIFrameElement) => {
    const doc = iframe.contentDocument;
    if (!doc) return { width: 0, height: 0 };

    const body = doc.body;
    const html = doc.documentElement;

    // 确保取到完整的内容尺寸（滚动尺寸优先）
    const width = Math.max(
        body.scrollWidth, body.offsetWidth,
        html.scrollWidth, html.offsetWidth, html.clientWidth,
    );
    const height = Math.max(
        body.scrollHeight, body.offsetHeight,
        html.scrollHeight, html.offsetHeight, html.clientHeight,
    );
    return { width, height };
};

// 更新 iframe 宽高（若尺寸变化）
let updating = false;
const updateSize = () => {
    const iframe = iframeRef.value;
    if (!iframe || !iframe.contentDocument || updating) return;

    updating = true;
    const { width, height } = getContentSize(iframe);
    if (width > 0 && height > 0 && (width !== iframeWidth.value || height !== iframeHeight.value)) {
        iframeWidth.value = width;
        iframeHeight.value = height;
    }
    updating = false;
};

// 设置内部样式，并在样式生效后获取尺寸
const setupIframe = async (iframe: HTMLIFrameElement) => {
    const doc = iframe.contentDocument;
    if (!doc) return;

    // 注入样式：禁止内部滚动条 + 强制内容完全展开
    const style = doc.createElement('style');
    style.textContent = `
    html, body {
        margin: 0 !important;
        padding: 0 !important;
        background-color: ${backgroundColor.value} !important;
        overflow: hidden !important;  /* 让 scrollWidth 等于真实内容宽度 */
    }
  `;
    doc.head.appendChild(style);

    // 等待一帧，确保样式被浏览器应用
    await new Promise((resolve) => requestAnimationFrame(resolve));

    // 初次获取尺寸
    updateSize();

    // 使用 ResizeObserver 监听 body/html 尺寸变化（内容增减、图片加载等）
    resizeObserver = new ResizeObserver(() => updateSize());
    resizeObserver.observe(doc.body);
    resizeObserver.observe(doc.documentElement);

    // 额外使用 MutationObserver 监听子树变化，防止某些 DOM 变化未触发 ResizeObserver
    mutationObserver = new MutationObserver(() => updateSize());
    mutationObserver.observe(doc.body, { childList: true, subtree: true, attributes: true });
    mutationObserver.observe(doc.documentElement, { childList: true, subtree: true, attributes: true });
};

// iframe 加载完成
const onIframeLoad = () => {
    const iframe = iframeRef.value;
    if (iframe && iframe.contentDocument) {
        setupIframe(iframe);
    }
};

// 清理
onUnmounted(() => {
    if (resizeObserver) {
        resizeObserver.disconnect();
        resizeObserver = null;
    }
    if (mutationObserver) {
        mutationObserver.disconnect();
        mutationObserver = null;
    }
});
</script>

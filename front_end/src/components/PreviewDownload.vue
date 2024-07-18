<template>
    <el-button :size="'small'" plain icon="View" @click="preview(id);">预览</el-button>
    <el-button :size="'small'" plain icon="Download" @click="download($event, id)">下载</el-button>
</template>

<script setup lang="ts" name="PreviewDownload">
// 拟弃用
// 两个按钮，预览或下载
import { onMounted, ref } from "vue";
// import axios from 'axios';
// import { getCurrentInstance } from 'vue';
import useCurrentInstance from "@/utils/common/useCurrentInstance";
import { preview } from "@/utils/common/PlayerDialog";

const { proxy } = useCurrentInstance();
// import { genFileId, ElMessage } from 'element-plus'

// const hashkey = ref("");

const { id } = defineProps({
    id: {
        type: Number,
    }
})


// // 1. 用户点击播放录像 0
// const id = 0

// // 2. 在重新创建弹窗前清空播放器对象
// window.flop = null

// // 3. 新建弹窗和 iframe

// // 4. 获取实际录像播放地址
// getUrl(id, (url) => {
//   // 5. 在回调中根据播放器状态决定如何播放录像
//   if (window.flop) {
//     window.flop.playVideo(url)
//   } else {
//     window.flop = {
//       onload: function () {
//         window.flop.playVideo(url)
//       }
//     }
//   }
// })

// function getUrl (id: number, onSuccess: (url: string) => void) {
//   // 录像播放地址
//   onSuccess(`https://example.com/${id}.avf`)
// }


const download = (event: MouseEvent, id: Number | undefined) => {
    if (!id) {
        return
    }
    const down = document.createElement('a');
    down.style.display = 'none';
    down.href = import.meta.env.VITE_BASE_API + "/video/download/?id=" + id;
    document.body.appendChild(down);
    down.click();
    URL.revokeObjectURL(down.href);
    document.body.removeChild(down);
}

// declare interface Window {
// 	flop: any
// }

onMounted(() => {

    // (window as any).flop = {
    // 	onload: ()=>{},
    // onload: () => {
    // 具体参数说明参见：https://github.com/hgraceb/flop-player#flopplayvideouri-options
    // (window as any).flop.playVideo(uri, {
    // 	share: {
    // 		uri: uri,
    // 		pathname: "/flop-player/player",
    // 		anonymous: false,
    // 		background: "rgba(100, 100, 100, 0.05)",
    // 		title: "Flop Player Share",
    // 		favicon: "https://avatars.githubusercontent.com/u/38378650?s=32", // 胡帝的头像
    // 	},
    // 	anonymous: false,
    // 	background: "rgba(0, 0, 0, 0)",
    // 	listener: function () {
    // 		preview_visible.value = false;
    // 	},
    // });
    // },
    // };
});


</script>

<style></style>
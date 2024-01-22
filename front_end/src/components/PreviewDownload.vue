<template>
	<Teleport to=".common-layout">
		<el-dialog v-model="preview_visible" style="background-color: rgba(240, 240, 240, 0.8);" draggable align-center 
		destroy-on-close :modal="false" :lock-scroll="false">
			<iframe class="flop-player-iframe flop-player-display-none" style="width: 100%; height: 500px; border: 0px"
				src="/flop/index.html" ref="video_iframe"></iframe>
		</el-dialog>
	</Teleport>
	<el-button :size="'small'" plain icon="View" @click="preview($event, id);">预览</el-button>
	<el-button :size="'small'" plain icon="Download" @click="download($event, id)">下载</el-button>
</template>

<script setup lang="ts" name="PreviewDownload">
// 两个按钮，预览或下载
import { defineProps } from 'vue';
import { onMounted, watch, ref, toRefs } from "vue";
// import axios from 'axios';
// import { getCurrentInstance } from 'vue';
import useCurrentInstance from "@/utils/common/useCurrentInstance";
const { proxy } = useCurrentInstance();
// import { genFileId, ElMessage } from 'element-plus'


const preview_visible = ref(false);
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

const preview = (event : MouseEvent, id: Number | undefined) => {
	if (!id) {
		return
	}
	(window as any).flop = null;
	preview_visible.value = true;
	proxy.$axios.get('/video/get_software/',
		{
			params: {
				id,
			}
		}
	).then(function (response) {
		let uri = process.env.VUE_APP_BASE_API + "/video/preview/?id=" + id;
		// console.log(uri);
		if (response.data.msg == "a") {
			uri += ".avf";
		} else if (response.data.msg == "e") {
			uri += ".evf";
		}
		// 等待 Flop Player 初始化完成
		(window as any).flop = {
			onload: () => {
				// 具体参数说明参见：https://github.com/hgraceb/flop-player#flopplayvideouri-options
				(window as any).flop.playVideo(uri, {
					share: {
						uri: uri,
						pathname: "/flop-player/player",
						anonymous: false,
						background: "rgba(100, 100, 100, 0.05)",
						title: "Flop Player Share",
						favicon: "https://avatars.githubusercontent.com/u/38378650?s=32", // 胡帝的头像
					},
					anonymous: false,
					background: "rgba(0, 0, 0, 0)",
					listener: function () {
						preview_visible.value = false;
					},
				});
			},
		};

	}).catch(
		(res) => {
			console.log(res);
		}
	)
}


const download = (event : MouseEvent, id: Number | undefined) => {
	if (!id) {
		return
	}
	const down = document.createElement('a');
	down.style.display = 'none';
	down.href = process.env.VUE_APP_BASE_API + "/video/download/?id=" + id;
	document.body.appendChild(down);
	down.click();
	URL.revokeObjectURL(down.href);
	document.body.removeChild(down);
}

declare interface Window {
	flop: any
}


onMounted(() => {


});


</script>
 
<style>

</style>
<template>
	<div class="canvas-box" :style="{ height: '32px' }">
		<!-- <canvas id="id-canvas2" class="id-canvas2" :width="contentWidth" :height="contentHeight"></canvas> -->
		<img :src="captchaUrl" alt="" @click="refreshPic()">
	</div>
</template>
 
<script setup lang="ts">
import { onMounted, watch, ref,toRefs } from "vue";
// import axios from 'axios';
// import {getCurrentInstance} from 'vue';
import useCurrentInstance from "@/utils/common/useCurrentInstance";
const {proxy} = useCurrentInstance();
// import { AXIOS_BASE_URL } from '../config';
// axios.defaults.headers['Content-Type'] = 'application/x-www-form-urlencoded';


const captchaUrl = ref("")
const hashkey = ref("")


const refreshPic = () => {
	proxy.$axios.get('/userprofile/refresh_captcha/')
		.then(function (response) {
			hashkey.value = response.data.hashkey;
			// console.log(hashkey.value);
			captchaUrl.value = process.env.VUE_APP_BASE_API + `/userprofile/captcha/image/` + hashkey.value;
			// console.log(captchaUrl.value);
		})
		.catch(function (error) {
			console.log(error);
		});
}

onMounted(() => {
	refreshPic();
});

// watch(
// 	() => props.hashkey,
// 	val => {
// 		// console.log(val);
// 		refreshPic();
// 	}
// );

// const { expose } =useContext()
// expose({
//     captchaUrl
//   })
defineExpose({
	hashkey,
	refreshPic
});

</script>
 
<style scoped>
.canvas-box {
	cursor: pointer;

	.id-canvas2 {
		height: 100%;
	}
}
</style>
<template>
	<div v-loading="loading" class="canvas-box" :style="{ height: '32px' }">
		<img :src="captchaUrl" alt="" @click="refreshPic()">
	</div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import useCurrentInstance from "@/utils/common/useCurrentInstance";
const { proxy } = useCurrentInstance();
import { ElMessage } from 'element-plus'

const captchaUrl = ref("")
const hashkey = ref("")
const loading = ref(true)

const refreshPic = () => {
	loading.value = true;
	proxy.$axios.get('/userprofile/refresh_captcha/').then(function (response) {
		if (response.data.status == 100) {
			hashkey.value = response.data.hashkey;
			captchaUrl.value = import.meta.env.VITE_BASE_API + `/userprofile/captcha/image/` + hashkey.value + "/";
		} else if (response.data.status >= 101) {
			ElMessage.error({ message: response.data.msg, offset: 68 });
		}
		loading.value = false;
	}).catch(function (error) {
		console.log(error);
	});
}

onMounted(() => {
	refreshPic();
});

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
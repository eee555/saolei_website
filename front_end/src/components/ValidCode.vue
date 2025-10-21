<template>
    <div class="canvas-box" :style="{ height: '32px' }" @click="refreshPic()">
        <el-text v-if="loading">
            {{ t('form.captchaLoading') }}
        </el-text>
        <img v-else-if="captchaUrl" :src="captchaUrl" alt="">
        <el-text v-else>
            {{ t('form.captchaLoadingFail') }}
        </el-text>
    </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { ElText } from 'element-plus';
import { httpErrorNotification, unknownErrorNotification } from './Notifications';
import { useI18n } from 'vue-i18n';

const { proxy } = useCurrentInstance();

const { t } = useI18n();

const captchaUrl = ref('');
const hashkey = ref('');
const loading = ref(true);

const refreshPic = () => {
    loading.value = true;
    proxy.$axios.get('/userprofile/refresh_captcha/').then(function (response) {
        if (response.data.status == 100) {
            hashkey.value = response.data.hashkey;
            captchaUrl.value = import.meta.env.VITE_BASE_API + '/userprofile/captcha/image/' + hashkey.value + '/';
        } else {
            unknownErrorNotification(response.data);
            captchaUrl.value = '';
        }
        loading.value = false;
    }).catch((error) => {
        httpErrorNotification(error);
        captchaUrl.value = '';
        loading.value = false;
    });
};

onMounted(() => {
    refreshPic();
});

defineExpose({
    hashkey,
    refreshPic,
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

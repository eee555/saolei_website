<template>
    <Teleport to=".common-layout">
        <el-dialog v-model="preview_visible"
            style="background-color: rgba(240, 240, 240, 0.48); backdrop-filter: blur(1px);" draggable align-center
            destroy-on-close :modal="false" :lock-scroll="false">
            <iframe v-if="preview_visible" class="flop-player-iframe flop-player-display-none" style="width: 100%; height: 500px; border: 0px"
                src="/flop/index.html" ref="video_iframe"></iframe>
        </el-dialog>
    </Teleport>
    <span v-if="data.id" @click="preview(data.id);" class="clickable">{{ data.text }}</span>
    <span v-else>--</span>
</template>

<script setup lang="ts" name="PreviewNumber">
// 某个数字或字符串，点击后预览
import { onMounted, watch, ref, toRefs } from "vue";
import useCurrentInstance from "@/utils/common/useCurrentInstance";
import { generalNotification } from "@/utils/system/status";
import { useI18n } from "vue-i18n";
const { proxy } = useCurrentInstance();
const preview_visible = ref(false);
const t = useI18n();

const data = defineProps({
    id: {
        type: Number,
    },
    text: {
        type: [String, Number],
    },
})



const preview = (id: Number | undefined) => {
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
        let uri = import.meta.env.VITE_BASE_API + "/video/preview/?id=" + id;
        // console.log(uri);
        if (response.data.msg == "a") {
            uri += ".avf";
        } else if (response.data.msg == "e") {
            uri += ".evf";
        }

        if ((window as any).flop) {
            playVideo(uri);
        } else {
            (window as any).flop = {
                onload: async function () {
                    playVideo(uri);
                },
            }
        }

    }).catch((error: any) => {
        generalNotification(t, error.response.status, t.t('common.action.getSoftware'))
    })
}

const playVideo = function (uri: string) {
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
            (window as any).flop = null;
        },
    });
}


</script>

<style>

</style>
<template>
    <el-dialog v-model="videoplayerstore.visible" style="backdrop-filter: blur(1px);" draggable align-center destroy-on-close
        :modal="false" :lock-scroll="false">
        <iframe class="flop-player-iframe flop-player-display-none" style="width: 100%; height: 500px; border: 0px"
            src="/flop/index.html" ref="video_iframe"></iframe>
    </el-dialog>
</template>

<script setup lang="ts">
// 播放录像的窗口
import { useVideoPlayerStore } from '@/store';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { watch } from 'vue';
import { generalNotification } from '@/utils/system/status';
import { useI18n } from 'vue-i18n';
const { proxy } = useCurrentInstance();
const videoplayerstore = useVideoPlayerStore();
const t = useI18n();

watch(videoplayerstore, () => {
    if (videoplayerstore.visible) {
        preview(videoplayerstore.id)
    }
})

const preview = (id: Number | undefined) => {
    if (!id) {
        return
    }
    (window as any).flop = null;
    proxy.$axios.get('/video/get_software/',
        {
            params: {
                id,
            }
        }
    ).then(function (response) {
        let url = import.meta.env.VITE_BASE_API + "/video/preview/?id=" + id;
        // console.log(url);
        if (response.data.msg == "a") {
            url += ".avf";
        } else if (response.data.msg == "e") {
            url += ".evf";
        }

        if ((window as any).flop) {
            playVideo(url);
        } else {
            (window as any).flop = {
                onload: async function () {
                    playVideo(url);
                },
            }
        }
    }).catch((error: any) => {
        generalNotification(t, error.response.status, t.t('common.action.getSoftware'))
    })
}

const playVideo = function (url: string) {
    (window as any).flop.playVideo(url, {
        share: {
            uri: url,
            pathname: "/flop-player/player",
            anonymous: false,
            background: "rgba(100, 100, 100, 0.05)",
            title: "Flop Player Share",
            favicon: "https://avatars.githubusercontent.com/u/38378650?s=32", // 胡帝的头像
        },
        anonymous: false,
        background: "rgba(0, 0, 0, 0)",
        listener: function () {
            videoplayerstore.visible = false;
            (window as any).flop = null;
        },
    });
}

</script>
<template>
    <span @click.stop>
        <el-popover
            v-if="render" :visible="visible" placement="bottom" width="298px"
            popper-class="max-h-300px overflow-auto" popper-style="z-index:888;" @show="pop_show" @hide="pop_hide"
        >
            <div>
                <div style="width: 80px;float: left;line-height: 200%;">
                    <el-image
                        style="width: 72px; height: 72px;margin-top: 10px;border-radius: 8px;" :src="image_url"
                        :fit="'cover'"
                    />
                    <el-button style="width: 72px;height: 24px;" @click="visit_me(userId);">我的空间</el-button>
                </div>
                <div v-loading="is_loading" style="width: 188px;float: right;text-align: center;line-height: 180%;">
                    <div><strong>{{ realname }}</strong> (id: {{ userId }})</div>
                    <div>初级纪录：<PreviewNumber :id="+b_t_id" :text="ms_to_s(b_t)" /> | <PreviewNumber :id="+b_bvs_id" :text="to_fixed_n(b_bvs, 3)" />
                    </div>
                    <div>中级纪录：<PreviewNumber :id="+i_t_id" :text="ms_to_s(i_t)" /> | <PreviewNumber :id="+i_bvs_id" :text="to_fixed_n(i_bvs, 3)" />
                    </div>
                    <div>高级纪录：<PreviewNumber :id="+e_t_id" :text="ms_to_s(e_t)" /> | <PreviewNumber :id="+e_bvs_id" :text="to_fixed_n(e_bvs, 3)" />
                    </div>
                    <div>总计纪录：
                        <span style="color: #BF9000;font-weight: bold;">{{ ms_to_s(b_t + i_t + e_t) }}</span>
                        |
                        <span style="color: #BF9000;font-weight: bold;">{{ to_fixed_n(b_bvs + i_bvs + e_bvs, 3)
                        }}</span>
                    </div>
                </div>

            </div>
            <template #reference>
                <el-link :underline="false" @click="visible = !visible;">{{ data.userName }}</el-link>
            </template>
        </el-popover>
        <el-link v-else :underline="false" @click="render = true; visible = true;">{{ data.userName }}</el-link>
    </span>
</template>

<script setup lang="ts" name="PlayerName">
// 用户的名字，鼠标移上去以后弹出气泡框，可以访问他的主页
import { ref } from 'vue';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
const { proxy } = useCurrentInstance();
import image_url_default from '@/assets/person.png';
const image_url = ref(image_url_default);
// import PreviewDownload from '@/components/PreviewDownload.vue';
import PreviewNumber from '@/components/PreviewNumber.vue';
import { useRouter } from 'vue-router';
import { ms_to_s, to_fixed_n } from '@/utils';
const router = useRouter();
import { store } from '../store';
import { ElLink, ElPopover, ElImage, ElButton, vLoading } from 'element-plus';

const data = defineProps({
    userId: {
        type: Number,
        default: 0,
    },
    userName: {
        type: String,
        default: '',
    },
});

const render = ref<boolean>(false); // 控制只渲染一次
const visible = ref<boolean>(false);
const is_loading = ref(true);

const realname = ref('');
const b_t = ref(999999);
const b_bvs = ref('');
const b_t_id = ref('');
const b_bvs_id = ref('');
const i_t = ref(999999);
const i_bvs = ref('');
const i_t_id = ref('');
const i_bvs_id = ref('');
const e_t = ref(999999);
const e_bvs = ref('');
const e_t_id = ref('');
const e_bvs_id = ref('');

const pop_show = async () => {
    if (data.userId === 0) return;
    document.addEventListener('mousedown', handleOutsideClick);
    is_loading.value = true;

    image_url.value = image_url_default;
    realname.value = '';

    await proxy.$axios.get('/msuser/info_abstract/',
        {
            params: {
                id: data.userId,
            },
        },
    ).then(function (response) {
        const response_data = response.data;
        realname.value = response_data.realname;
        if (response_data.avatar) {
            image_url.value = 'data:image/;base64,' + response_data.avatar;
        }

        const records = JSON.parse(response_data.record_abstract);

        b_t.value = records.timems[0];
        i_t.value = records.timems[1];
        e_t.value = records.timems[2];

        b_t_id.value = records.timems_id[0];
        i_t_id.value = records.timems_id[1];
        e_t_id.value = records.timems_id[2];
        b_bvs.value = records.bvs[0];
        i_bvs.value = records.bvs[1];
        e_bvs.value = records.bvs[2];
        b_bvs_id.value = records.bvs_id[0];
        i_bvs_id.value = records.bvs_id[1];
        e_bvs_id.value = records.bvs_id[2];

        is_loading.value = false;
    }).catch(() => {
        // is_loading.value = false;
    });
};

// 用户记录小弹窗关闭后，删除其中的数据
const pop_hide = () => {
    document.removeEventListener('mousedown', handleOutsideClick);
    image_url.value = image_url_default;
    realname.value = '';
    i_t.value = 999999;
    b_t.value = 999999;
    e_t.value = 999999;
    b_t_id.value = '';
    i_t_id.value = '';
    e_t_id.value = '';
    b_bvs.value = '';
    i_bvs.value = '';
    e_bvs.value = '';
    b_bvs_id.value = '';
    i_bvs_id.value = '';
    e_bvs_id.value = '';
    is_loading.value = true;
};

const visit_me = (user_id: number) => {
    // proxy.$store.commit('updatePlayer', { "id": id.value, "realname":realname.value });
    // localStorage.setItem("player", JSON.stringify({ "id": id.value, "realname":realname.value }));
    // localStorage.setItem("player", JSON.stringify({ "id": id.value }));
    store.player.id = user_id;
    router.push({ name: 'player_id', params: { id: user_id } });
};

// 实现点旁边时候关闭气泡
const handleOutsideClick = (event: any) => {
    const componentElement = document.querySelector('.el-popover');
    if (!componentElement?.contains(event.target)) {
        visible.value = false;
    }
};



</script>

<style lang="less" scoped></style>

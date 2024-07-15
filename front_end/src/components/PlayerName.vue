<template>
    <span @click.stop>
        <el-popover v-if="render" v-model="visible" placement="bottom" width="298px" popper-class="max-h-300px overflow-auto" @show="pop_show"
            @hide="pop_hide" popper-style="z-index:888;" 
            :show-after="0" :hide-after="0">
            <Wait v-show="is_loading"></Wait>
            <div>
                <div style="width: 80px;float: left;line-height: 200%;">
                    <el-image style="width: 72px; height: 72px;margin-top: 10px;border-radius: 8px;" :src="image_url"
                        :fit="'cover'" />
                    <el-button style="width: 72px;height: 24px;" @click="visit_me(+id);">我的空间</el-button>
                </div>
                <div style="width: 188px;float: right;text-align: center;line-height: 180%;">
                    <div><strong>{{ realname }}</strong> (id: {{ id }})</div>
                    <div>初级纪录：<PreviewNumber :id="+b_t_id" :text="to_fixed_n(b_t, 3)">
                        </PreviewNumber> | <PreviewNumber :id="+b_bvs_id" :text="to_fixed_n(b_bvs, 3)">
                        </PreviewNumber>
                    </div>
                    <div>中级纪录：<PreviewNumber :id="+i_t_id" :text="to_fixed_n(i_t, 3)">
                        </PreviewNumber> | <PreviewNumber :id="+i_bvs_id" :text="to_fixed_n(i_bvs, 3)">
                        </PreviewNumber>
                    </div>
                    <div>高级纪录：<PreviewNumber :id="+e_t_id" :text="to_fixed_n(e_t, 3)">
                        </PreviewNumber> | <PreviewNumber :id="+e_bvs_id" :text="to_fixed_n(e_bvs, 3)">
                        </PreviewNumber>
                    </div>
                    <div>总计纪录：
                        <span style="color: #BF9000;font-weight: bold;">{{ to_fixed_n(b_t + i_t + e_t, 3) }}</span>
                        |
                        <span style="color: #BF9000;font-weight: bold;">{{ to_fixed_n(b_bvs + i_bvs + e_bvs, 3)
                            }}</span>
                    </div>
                </div>

            </div>
            <template #reference>
                <span href="" target="_blank" class="clickable" @click="visible = !visible">{{ data.user_name }}
                </span>
            </template>
        </el-popover> 
        <span v-else href="" target="_blank" class="clickable" @click="render = true; visible = true">{{ data.user_name }}
        </span>
    </span>
</template>

<script setup lang="ts" name="PlayerName">
// 用户的名字，鼠标移上去以后弹出气泡框，可以访问他的主页
import { onMounted, watch, ref, toRefs } from "vue";
import { getCurrentInstance } from 'vue';
import useCurrentInstance from "@/utils/common/useCurrentInstance";
const { proxy } = useCurrentInstance();
import { genFileId, ElMessage } from 'element-plus'
import image_url_default from '@/assets/person.png';
const image_url = ref(image_url_default);
// import PreviewDownload from '@/components/PreviewDownload.vue';
import PreviewNumber from '@/components/PreviewNumber.vue';
import Wait from '@/components/Wait.vue';
import { useRouter } from 'vue-router'
import { ms_to_s } from "@/utils"
const router = useRouter()
import { useUserStore } from '../store'
const store = useUserStore()


const data = defineProps({
    user_id: {
        type: Number,
    },
    user_name: {
        type: String,
    },
})

const render = ref<Boolean>(false);
const visible = ref<Boolean>(false);

const realname = ref("");
const id = ref("");
const b_t = ref("");
const b_bvs = ref("");
const b_t_id = ref("");
const b_bvs_id = ref("");
const i_t = ref("");
const i_bvs = ref("");
const i_t_id = ref("");
const i_bvs_id = ref("");
const e_t = ref("");
const e_bvs = ref("");
const e_t_id = ref("");
const e_bvs_id = ref("");

// 控制加载时的小圈圈
const is_loading = ref(true);


const pop_show = () => {
    image_url.value = image_url_default;
    realname.value = "";
    id.value = "";

    proxy.$axios.get('/msuser/info_abstract/',
        {
            params: {
                id: data.user_id,
            }
        }
    ).then(function (response) {

        const response_data = response.data;
        id.value = data.user_id + "";
        realname.value = response_data.realname;
        if (response_data.avatar) {
            image_url.value = "data:image/;base64," + response_data.avatar;
        }
        
        const records = JSON.parse(response_data.record_abstract)

        b_t.value = ms_to_s(records.timems[0])
        i_t.value = ms_to_s(records.timems[1])
        e_t.value = ms_to_s(records.timems[2])
        
        b_t_id.value = records.timems_id[0]
        i_t_id.value = records.timems_id[1]
        e_t_id.value = records.timems_id[2]
        b_bvs.value = records.bvs[0]
        i_bvs.value = records.bvs[1]
        e_bvs.value = records.bvs[2]
        b_bvs_id.value = records.bvs_id[0]
        i_bvs_id.value = records.bvs_id[1]
        e_bvs_id.value = records.bvs_id[2]

        is_loading.value = false;
    }).catch(() => {
        // is_loading.value = false;
    })


}


// 用户记录小弹窗关闭后，删除其中的数据
const pop_hide = () => {
    image_url.value = image_url_default;
    realname.value = "";
    id.value = "";
    i_t.value = "";
    b_t.value = "";
    e_t.value = "";
    b_t_id.value = "";
    i_t_id.value = "";
    e_t_id.value = "";
    b_bvs.value = "";
    i_bvs.value = "";
    e_bvs.value = "";
    b_bvs_id.value = "";
    i_bvs_id.value = "";
    e_bvs_id.value = "";
}

function to_fixed_n(input: string | number | undefined, to_fixed: number): string | number | undefined {
    // 返回保留to_fixed位小数的字符串，四舍六入五取双
    if (input === undefined) {
        return input;
    }
    if (to_fixed <= 0) {
        return input;
    }
    if (typeof (input) == "string") {
        return parseFloat(input).toFixed(to_fixed);
    }
    return (input as number).toFixed(to_fixed);
}

const visit_me = (user_id: Number) => {
    // proxy.$store.commit('updatePlayer', { "id": id.value, "realname":realname.value });
    // localStorage.setItem("player", JSON.stringify({ "id": id.value, "realname":realname.value }));
    // localStorage.setItem("player", JSON.stringify({ "id": id.value }));
    store.player.id = +id.value;
    router.push(`player\/${store.player.id}`)
}

</script>

<style lang="less" scoped>
.clickable:hover {
    color: rgb(26, 127, 228);
    cursor: pointer;
}
</style>
<template>
    <el-tabs>
        <el-tab-pane>
            <template #label>
                <BaseIconMetasweeper />
            </template>
            <el-text>
                设置正确的比赛标识，上传录像时即可自动参赛。
            </el-text>
        </el-tab-pane>
        <el-tab-pane>
            <template #label>
                <BaseIconArbiter />
            </template>
            <el-text v-if="token === ''">
                请在比赛标识公布后，先在这里注册参赛标识，然后上传使用该标识的录像。
            </el-text>
            <el-text v-else-if="personaltoken === ''">
                请先在这里注册参赛标识，然后上传使用该标识的录像。参赛标识必须以{{ token }}结尾，例如
                <span style="font-family: 'Courier New', Courier, monospace;">Guo Jin Yang {{ token }}</span>
                <el-input v-model="newPersonaltoken" placeholder="参赛标识" />
                <el-button @click="registerToken">
                    注册
                </el-button>
                <el-text v-if="errorText !== ''" type="danger">
                    {{ errorText }}
                </el-text>
            </el-text>
            <el-text v-else>
                您的参赛标识为
                <span style="font-family: 'Courier New', Courier, monospace;">{{ personaltoken }}</span>
                &nbsp;
                <IconCopy :text="personaltoken" />
                <br>
                个人主页上传的对应标识的录像将自动归入比赛录像。
            </el-text>
        </el-tab-pane>
    </el-tabs>
</template>

<script setup lang="ts">

import { ElTabs, ElTabPane, ElText, ElInput, ElButton } from 'element-plus';
import IconCopy from '@/components/widgets/IconCopy.vue';
import { ref } from 'vue';
import { httpErrorNotification, successNotification, unknownErrorNotification } from '@/components/Notifications';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import BaseIconArbiter from '@/components/common/BaseIconArbiter.vue';
import BaseIconMetasweeper from '@/components/common/BaseIconMetasweeper.vue';

const props = defineProps({
    order: {
        type: Number,
        default: 0,
    },
    token: {
        type: String,
        default: '',
    },
});

const personaltoken = defineModel({
    type: String,
    default: '',
});

const { proxy } = useCurrentInstance();

const errorText = ref<string>('');
const newPersonaltoken = ref<string>('');

function registerToken() {
    proxy.$axios.post('tournament/gscregister/', {
        token: newPersonaltoken.value,
        order: props.order,
    }).then((response) => {
        const data = response.data;
        switch (data.type) {
            case 'success':
                successNotification(response);
                personaltoken.value = newPersonaltoken.value;
                newPersonaltoken.value = '';
                break;
            case 'error':
                switch (data.category) {
                    case 'suffix': errorText.value = '后缀错误'; break;
                    case 'collision': errorText.value = '标识被占用'; break;
                    case 'invalid': errorText.value = '标识违规'; break;
                    default: unknownErrorNotification(response);
                }
                break;
            default:
                unknownErrorNotification(response);
        }
    }).catch(httpErrorNotification);
}

</script>

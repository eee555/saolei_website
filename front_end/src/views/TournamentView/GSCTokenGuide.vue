<template>
    <el-tabs>
        <el-tab-pane>
            <template #label>
                <BaseIconMetasweeper />
            </template>
            <el-text v-if="token === ''">
                {{ t('gsc.identifierGuide.metasweeper.preparing') }}
            </el-text>
            <el-text v-else>
                {{ t('gsc.identifierGuide.metasweeper.ongoing_1') }}
                <span class="ttfamily">{{ token }}</span>
                <IconCopy :text="token" />
                {{ t('gsc.identifierGuide.metasweeper.ongoing_2') }}
            </el-text>
        </el-tab-pane>
        <el-tab-pane>
            <template #label>
                <BaseIconArbiter />
            </template>
            <el-text v-if="token === ''">
                {{ t('gsc.identifierGuide.arbiter.preparing') }}
            </el-text>
            <el-text v-else-if="identifier === ''">
                {{ t('gsc.identifierGuide.arbiter.ongoing_pre1') }}
                <span class="ttfamily">{{ token }}</span>
                <IconCopy :text="token" />
                {{ t('gsc.identifierGuide.arbiter.ongoing_pre2') }}
                <span class="ttfamily">Guo Jin Yang {{ token }}</span>
                <el-input v-model="newIdentifier" placeholder="参赛标识" />
                <el-button @click="registerToken">
                    {{ t('common.button.register') }}
                </el-button>
                <el-text v-if="errorText !== ''" type="danger">
                    {{ errorText }}
                </el-text>
            </el-text>
            <el-text v-else>
                {{ t('gsc.identifierGuide.arbiter.ongoing_post1') }}
                <span class="ttfamily">{{ identifier }}</span>
                &nbsp;
                <IconCopy :text="identifier" />
                {{ t('gsc.identifierGuide.arbiter.ongoing_post2') }}
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
import { useI18n } from 'vue-i18n';

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

const identifier = defineModel({
    type: String,
    default: '',
});

const { proxy } = useCurrentInstance();
const { t } = useI18n();

const errorText = ref<string>('');
const newIdentifier = ref<string>('');

function registerToken() {
    proxy.$axios.post('tournament/gscregister/', {
        identifier: newIdentifier.value,
        order: props.order,
    }).then((response) => {
        const data = response.data;
        switch (data.type) {
            case 'success':
                successNotification(response);
                identifier.value = newIdentifier.value;
                newIdentifier.value = '';
                break;
            case 'error':
                switch (data.category) {
                    case 'suffix': errorText.value = t('msg.identifierIncorrectSuffix'); break;
                    case 'collision': errorText.value = t('msg.identifierOccupied'); break;
                    case 'invalid': errorText.value = t('msg.identifierIllegal'); break;
                    default: unknownErrorNotification(response);
                }
                break;
            default:
                unknownErrorNotification(response);
        }
    }).catch(httpErrorNotification);
}

</script>

<style scoped>

.ttfamily {
    font-family: 'Courier New', Courier, monospace;
}

</style>

<template>
    <el-tabs>
        <el-tab-pane>
            <template #label>
                <SoftwareIcon software="e" />
            </template>
            <span v-if="token === ''" class="text">
                {{ t('gsc.identifierGuide.metasweeper.preparing') }}
            </span>
            <span v-else class="text">
                {{ t('gsc.identifierGuide.metasweeper.ongoing_1') }}
                <span class="ttfamily">{{ token }}</span>
                <IconCopy :text="token" />
                {{ t('gsc.identifierGuide.metasweeper.ongoing_2') }}
            </span>
        </el-tab-pane>
        <el-tab-pane>
            <template #label>
                <SoftwareIcon software="a" />
            </template>
            <span v-if="token === ''" class="text">
                {{ t('gsc.identifierGuide.arbiter.preparing') }}
            </span>
            <span v-else-if="identifier === ''" class="text">
                {{ t('gsc.identifierGuide.arbiter.ongoing_pre1') }}
                <span class="ttfamily">{{ token }}</span>
                <IconCopy :text="token" />
                {{ t('gsc.identifierGuide.arbiter.ongoing_pre2') }}
                <span class="ttfamily">Guo Jin Yang {{ token }}</span>
                <el-input v-model="newIdentifier" placeholder="参赛标识" />
                <el-button @click="registerToken">
                    {{ t('common.button.register') }}
                </el-button>
                <span v-if="errorText !== ''" class="text text-danger">
                    {{ errorText }}
                </span>
            </span>
            <span v-else class="text">
                {{ t('gsc.identifierGuide.arbiter.ongoing_post1') }}
                <span class="ttfamily">{{ identifier }}</span>
                &nbsp;
                <IconCopy :text="identifier" />
                {{ t('gsc.identifierGuide.arbiter.ongoing_post2') }}
            </span>
        </el-tab-pane>
    </el-tabs>
</template>

<script setup lang="ts">

import { ElButton, ElInput, ElTabPane, ElTabs } from 'element-plus';
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';

import '@/styles/text.css';
import { httpErrorNotification, successNotification, unknownErrorNotification } from '@/components/Notifications';
import IconCopy from '@/components/widgets/IconCopy.vue';
import SoftwareIcon from '@/components/widgets/SoftwareIcon.vue';
import useCurrentInstance from '@/utils/common/useCurrentInstance';

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

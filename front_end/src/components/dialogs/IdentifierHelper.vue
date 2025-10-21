<template>
    <el-text size="large">
        <ul>
            <li>
                {{ t('helper.identifier.line_1_1') }}<BaseIconArbiter />{{ t('helper.identifier.line_1_2') }}<BaseIconMetasweeper />{{ t('helper.identifier.line_1_3') }}
            </li>
            <li>
                {{ t('helper.identifier.line_2_1') }}
            </li>
            <li>
                {{ t('helper.identifier.line_3_1') }}<VideoStateIcon state="d" />{{ t('helper.identifier.line_3_2') }}
            </li>
            <li>
                {{ t('helper.identifier.line_4_1') }}
                <ul>
                    <li>
                        {{ t('helper.identifier.line_4_2') }}
                    </li>
                    <li>
                        {{ t('helper.identifier.line_4_3') }}
                    </li>
                </ul>
                {{ t('helper.identifier.line_4_4') }}
            </li>
        </ul>
    </el-text>
</template>

<script lang="ts" setup>

import { ElText } from 'element-plus';
import { useI18n } from 'vue-i18n';

import BaseIconArbiter from '../common/BaseIconArbiter.vue';
import BaseIconMetasweeper from '../common/BaseIconMetasweeper.vue';
import VideoStateIcon from '../widgets/VideoStateIcon.vue';

const { t } = useI18n();

</script>

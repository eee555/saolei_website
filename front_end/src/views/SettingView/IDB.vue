<template>
    <div class="text text-small" style="margin-bottom: 1em">
        {{ t('local.tooltip') }}
    </div>
    <table class="el-table">
        <thead class="el-table__header">
            <tr class="el-table__row">
                <th class="el-table__cell">
                    {{ t('local.tableName') }}
                </th>
                <th class="el-table__cell">
                    {{ t('local.updateInterval') }}
                </th>
                <th class="el-table__cell">
                    {{ t('local.lastUpdate') }}
                </th>
                <th class="el-table__cell">
                    {{ t('local.batchSize') }}
                </th>
                <th class="el-table__cell">
                    {{ t('local.batchDelay') }}
                </th>
            </tr>
        </thead>
        <tbody class="el-table__body">
            <tr class="el-table__row">
                <td class="el-table__cell text-small" :title="t('local.userInfoTooltip')">
                    {{ t('local.userInfo') }}
                </td>
                <td class="el-table__cell" title="500~">
                    <InputNumber v-model="serviceConfig.userInfoUpdateInterval" :min="500" class="base-input" />
                </td>
                <td class="el-table__cell text-small">
                    {{ toISODateTimeString(new Date(serviceConfig.userInfoLastUpdate)) }}
                </td>
                <td class="el-table__cell" title="1~500">
                    <InputNumber v-model="serviceConfig.userInfoBatchSize" :min="1" :max="500" class="base-input" />
                </td>
                <td class="el-table__cell" title="500~">
                    <InputNumber v-model="serviceConfig.userInfoBatchDelay" :min="500" class="base-input" />
                </td>
            </tr>
        </tbody>
    </table>
</template>

<script setup lang="ts">
import '@/styles/text.css';

import { useI18n } from 'vue-i18n';

import InputNumber from '@/components/common/InputNumber.vue';
import { serviceConfig } from '@/services/store';
import { toISODateTimeString } from '@/utils/datetime';

const i18nMessages = {
    'zh-cn': { local: {
        batchDelay: '批量延迟',
        batchSize: '批量大小',
        lastUpdate: '上次刷新',
        tableName: '数据表',
        updateInterval: '刷新周期',
        userInfo: '用户基本数据',
        userInfoTooltip: '不包含头像、标识、账号绑定、纪录、录像数据',
        tooltip: "网页使用Indexed Database缓存部分数据，提升页面加载速度。当服务器数据更新时网页也需要更新，“@:{'local.updateInterval'}”就是网页向服务器请求更新数据的间隔，单位毫秒。如果一次需要更新大量数据，受到URL长度限制，只能分批次更新，“@:{'local.batchSize'}”是每批更新的条目数量，“@:{'local.batchDelay'}”是相邻批次之间的时间间隔，单位毫秒。", // eslint-disable-line @stylistic/quotes
    } },
    'en': { local: {
        batchDelay: 'Batch Delay',
        batchSize: 'Batch Size',
        lastUpdate: 'Last Update',
        tableName: 'Data Table',
        updateInterval: 'Update Interval',
        userInfo: 'User Info',
        userInfoTooltip: 'Excluding avatar, identifiers, account links, records, and videos',
        tooltip: "The webpage uses Indexed Database for caching to improve loading experience. The webpage needs to request for data updates occasionally, which is controlled by \"@:{'local.updateInterval'}\", in milliseconds. If a large amount of data needs to be updated, they need to be splitted into batches due to the URL length limits. \"@:{'local.batchSize'}\" is the number of items in each batch, and \"@:{'local.batchDelay'}\" is the time interval between consecutive batches, in milliseconds.", // eslint-disable-line @stylistic/quotes
    } },
};

const { t } = useI18n({ messages: i18nMessages });
</script>

<style lang="less" scoped>
.el-table__cell {
    padding: 0;
}

.base-input {
    field-sizing: content;
}
</style>

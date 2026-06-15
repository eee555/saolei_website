<template>
    <BaseCardNormal>
        <div style="margin-bottom: 0.5em;">
            <PrToolbar>
                <template #start>
                    <span class="text text-medium">
                        Minesweeper.Online&nbsp;#{{ id }}
                    </span>
                </template>
                <template #end>
                    <CarouselControl :ref-carousel="refCarousel" :length="carouselLength" />
                </template>
            </PrToolbar>
        </div>
        <ElCarousel v-if="verified" ref="refCarousel" trigger="click" :autoplay="false" indicator-position="none" :loop="false" arrow="never">
            <ElCarouselItem>
                <ElDescriptions border>
                    <ElDescriptionsItem :label="t('common.prop.update_time')" :span="3">
                        {{ utc_to_local_format(info.update_time) }}
                    </ElDescriptionsItem>
                    <ElDescriptionsItem :label="t('local.trophy')" :span="3">
                        {{ info.trophy }}
                    </ElDescriptionsItem>
                    <ElDescriptionsItem :label="t('common.prop.time')" :span="3">
                        {{ ms_to_s(info.b_t_ms) }} | {{ ms_to_s(info.i_t_ms) }} | {{ ms_to_s(info.e_t_ms) }}
                    </ElDescriptionsItem>
                    <ElDescriptionsItem :label="t('common.prop.ioe')" :span="3">
                        {{ maybeUndefinedToFixed(info.b_ioe, 2) }} | {{ maybeUndefinedToFixed(info.i_ioe, 2) }} | {{ maybeUndefinedToFixed(info.e_ioe, 2) }}
                    </ElDescriptionsItem>
                    <ElDescriptionsItem :label="t('common.prop.mastery')" :span="3">
                        {{ maybeUndefined(info.b_mastery) }} | {{ maybeUndefined(info.i_mastery) }} | {{ maybeUndefined(info.e_mastery) }}
                    </ElDescriptionsItem>
                    <ElDescriptionsItem :label="t('common.prop.winstreak')" :span="3">
                        {{ maybeUndefined(info.b_winstreak) }} | {{ maybeUndefined(info.i_winstreak) }} | {{ maybeUndefined(info.e_winstreak) }}
                    </ElDescriptionsItem>
                    <ElDescriptionsItem :label="t('local.maxDifficulty')" :span="3">
                        {{ info.max_difficulty }}
                    </ElDescriptionsItem>
                </ElDescriptions>
            </ElCarouselItem>
            <ElCarouselItem>
                <ElDescriptions border>
                    <ElDescriptionsItem :label="t('local.experience')" :span="3">
                        {{ info.experience }}
                    </ElDescriptionsItem>
                    <ElDescriptionsItem :label="t('local.arenaPoint')" :span="3">
                        {{ info.arena_point }}
                    </ElDescriptionsItem>
                    <ElDescriptionsItem :label="t('local.win')" :span="3">
                        {{ info.win }}
                    </ElDescriptionsItem>
                    <ElDescriptionsItem :label="t('local.lastSeason')" :span="3">
                        {{ info.last_season }}
                    </ElDescriptionsItem>
                    <ElDescriptionsItem :label="t('local.resource')" :span="3">
                        <ElImage src="https://minesweeper.online/img/other/hp.svg" class="icon" /><span class="text">
                            {{ info.honour }}
                        </span>&nbsp;
                        <ElImage src="https://minesweeper.online/img/other/coin.svg" class="icon" /><span class="text">
                            {{ info.minecoin }}
                        </span>&nbsp;
                        <ElImage src="https://minesweeper.online/img/gems/0.svg" class="icon" /><span class="text">
                            {{ info.gem }}
                        </span>&nbsp;
                        <ElImage src="https://minesweeper.online/img/arena-coins/0.svg" class="icon" /><span class="text">
                            {{ info.coin }}
                        </span>&nbsp;
                        <Ticket class="icon" /><span class="text">
                            {{ info.arena_ticket }}
                        </span>&nbsp;
                        <ElImage src="https://minesweeper.online/img/eq.svg" class="icon" /><span class="text">
                            {{ info.equipment }}
                        </span>&nbsp;
                        <ElImage src="https://minesweeper.online/img/item/parts0.svg" class="icon" /><span class="text">
                            {{ info.part }}
                        </span>&nbsp;
                    </ElDescriptionsItem>
                </ElDescriptions>
            </ElCarouselItem>
            <ElCarouselItem v-if="store.user.id == store.player.id">
                <div>
                    <span class="text text-large">
                        {{ t('accountlink.statSummary') }}
                    </span>
                    &nbsp;
                    <ElButton @click="updateLink(); $emit('refresh')">
                        {{ t('accountlink.synchronize') }}
                    </ElButton>
                    &nbsp;
                    <IconTaskStatus :status="taskStatus" />
                    <br>
                    <span class="text text-danger text-small">
                        {{ errorMsg }}
                    </span>
                </div>
            </ElCarouselItem>
        </ElCarousel>
        <UnverifiedNotice v-else />
    </BaseCardNormal>
</template>

<script setup lang="ts">
import { ElButton, ElCarousel, ElCarouselItem, ElDescriptions, ElDescriptionsItem, ElImage } from 'element-plus';
import PrToolbar from 'primevue/toolbar';
import { computed, PropType, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import CarouselControl from './CarouselControl.vue';
import UnverifiedNotice from './UnverifiedNotice.vue';
import { AccountWoM, AccountWoMDefault } from './utils';

import BaseCardNormal from '@/components/common/BaseCardNormal.vue';
import IconTaskStatus from '@/components/common/IconTaskStatus.vue';
import { httpErrorNotification } from '@/components/Notifications';
import { store } from '@/store';
import { ms_to_s } from '@/utils';
import { TaskStatus } from '@/utils/common/structInterface';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { utc_to_local_format } from '@/utils/system/tools';

defineProps({
    id: { type: String, default: '0' },
    verified: { type: Boolean, default: false },
    info: {
        type: Object as PropType<AccountWoM>,
        default: () => AccountWoMDefault,
    },
});

defineEmits(['refresh']);

const { proxy } = useCurrentInstance();

const refCarousel = ref<typeof ElCarousel>();
const errorMsg = ref('');
const taskStatus = ref<TaskStatus>('');
const carouselLength = computed(() => store.player.id == store.user.id ? 3 : 2);

function maybeUndefined(value: any) {
    return value === undefined ? '-' : value;
}

function maybeUndefinedToFixed(value: number | undefined, fractionDigits?: number) {
    return value === undefined ? '-' : value.toFixed(fractionDigits);
}

async function updateLink() {
    taskStatus.value = 'loading';
    await proxy.$axios.post('accountlink/update/', {
        platform: 'w',
    }).then(function (response) {
        const data = response.data;
        errorMsg.value = '';
        taskStatus.value = data.type;
        if (data.type == 'error') {
            errorMsg.value = t(`errorMsg.${data.object}.title`) + t('common.punct.colon') + t(`errorMsg.${data.object}.${data.category}`);
        }
    }).catch(function (error) {
        errorMsg.value = '';
        taskStatus.value = 'error';
        httpErrorNotification(error);
    });
}

/* 本地化 Localization */
const i18nMessage = {
    'zh-cn': { local: {
        arenaPoint: '竞技场',
        experience: '经验',
        lastSeason: '最近赛季',
        maxDifficulty: '高难',
        resource: '资源',
        trophy: '奖杯',
        win: '总胜场',
    } },
    'en': { local: {
        arenaPoint: 'Arena',
        experience: 'Experience',
        lastSeason: 'Last Season',
        maxDifficulty: 'Max Difficulty',
        resource: 'Resources',
        trophy: 'Trophies',
        win: 'Wins',
    } },
};

const { t } = useI18n({ messages: i18nMessage });
</script>

<style lang="less" scoped>
.icon {
    height: 18px;
    vertical-align: middle;
}
</style>

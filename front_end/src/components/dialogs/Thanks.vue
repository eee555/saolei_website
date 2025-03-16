<template>
    <el-link @click="centerDialogVisible = true;">
        {{ t('footer.team') }}
    </el-link>
    <el-dialog 
        v-model="centerDialogVisible" :title="t('team.title')" width="700px" align-center draggable
        :lock-scroll="false"
    >
        <div style="padding-bottom: 5px">
            <strong>{{ t('team.owner') }}</strong>
        </div>
        <div>
            <GitHubUser username="eee555" />
        </div>
        <div style="padding-bottom: 5px; margin-top: 15px">
            <strong>{{ t('team.moderator') }}</strong>
        </div>
        <div>少年</div>
        <div>GodnuX</div>
        <div>auk ;-;</div>
        <el-divider />
        <el-row>
            <el-col :span="8">
                <div style="padding-bottom: 5px">
                    <strong>{{ t('team.software') }}</strong>
                </div>
                <div>
                    <GitHubUser username="eee555" />
                </div>
                <div>
                    <GitHubUser username="putianyi889" />
                </div>
                <div>
                    <GitHubUser username="ljzloser" />
                </div>
                <div>
                    <GitHubUser username="hwatson381" />
                </div>
                <div>
                    <GitHubUser username="hgraceb" />
                </div>
            </el-col>
            <el-col :span="8">
                <div style="padding-bottom: 5px">
                    <strong>{{ t('team.localization') }}</strong>
                </div>
                <div>
                    {{ t('team.zhCn') }}　
                    <GitHubUser username="putianyi889" />
                </div>
                <div>
                    {{ t('team.en') }}　
                    <GitHubUser username="putianyi889" />
                </div>
                <div>
                    {{ t('team.de') }}　
                    <GitHubUser username="auk3" />
                </div>
                <div>
                    {{ t('team.pl') }}　
                    <GitHubUser username="kiraa96" />
                </div>
            </el-col>
            <el-col :span="8">
                <div style="padding-bottom: 5px">
                    <strong>{{ t('team.designer') }}</strong>
                </div>
                <div>
                    <GitHubUser username="eee555" />
                </div>
                <div>
                    <GitHubUser username="putianyi889" />
                </div>
            </el-col>
        </el-row>
        <el-divider />
        <div style="padding-bottom: 5px">
            <strong>{{ t('team.acknowledgement') }}</strong>
        </div>
        <span v-for="item in acknowledgements" style="padding-right: 10px">
            {{ item.text }}
        </span>
    </el-dialog>
</template>

<script lang="ts" setup>
// 注册、登录的弹框及右上方按钮
import { ref } from 'vue'
import { ElDialog, ElDivider, ElRow, ElCol, ElLink } from 'element-plus';
import GitHubUser from '../widgets/GitHubUser.vue'

import { useI18n } from 'vue-i18n';
const { t } = useI18n();

const centerDialogVisible = ref(false);


// 积分系统完成后需要加jsd
const acknowledgements = [
    { text: 'T0nyX1ang' },
    { text: 'Pulsar' },
    { text: 'darkness' },
    { text: 'lc4337' },
    { text: '冰糖雪梨' },
    { text: '生命★是┗ 〓┛是☆什么' },
    { text: 'Arya' },
]

</script>


<style></style>

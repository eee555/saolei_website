<template>
    <el-tabs v-model="activeTab">
        <el-tab-pane label="用户信息" name="userprofile" lazy>
            <StaffUserProfile />
        </el-tab-pane>
        <el-tab-pane label="录像信息" name="videomodel" lazy>
            <StaffVideoModel />
        </el-tab-pane>
        <el-tab-pane label="账号绑定" name="accountlink" lazy>
            <StaffAccountLink />
        </el-tab-pane>
        <el-tab-pane label="标识管理" name="identifier" lazy>
            <StaffIdentifier />
        </el-tab-pane>
        <el-tab-pane label="录像批量更新" name="batchupdate" lazy>
            <StaffBatchUpdateVideo />
        </el-tab-pane>
        <el-tab-pane label="后台日志" name="logs" lazy>
            <StaffLogs />
        </el-tab-pane>
        <el-tab-pane label="比赛管理" name="tournament" lazy>
            <StaffTournament />
        </el-tab-pane>
        <el-tab-pane label="后台任务" name="task" lazy>
            <StaffTask />
        </el-tab-pane>
    </el-tabs>
</template>

<script lang="ts" setup>
// 管理员操作接口，通过'/staff'访问
import { ElTabPane, ElTabs } from 'element-plus';
import { ref } from 'vue';

import StaffAccountLink from './AccountLink.vue';
import StaffBatchUpdateVideo from './BatchUpdateVideo.vue';
import StaffIdentifier from './Identifier.vue';
import StaffLogs from './Logs.vue';
import StaffTask from './Task.vue';
import StaffTournament from './Tournament.vue';
import StaffUserProfile from './UserProfile.vue';
import StaffVideoModel from './VideoModel.vue';

const activeTab = ref('userprofile');

</script>

<template>
    <el-tabs v-model="activeTab">
        <el-tab-pane label="用户信息" name="userprofile">
            <StaffUserProfile />
        </el-tab-pane>
        <el-tab-pane label="录像信息" name="videomodel">
            <StaffVideoModel />
        </el-tab-pane>
        <el-tab-pane label="账号绑定" name="accountlink">
            <StaffAccountLink />
        </el-tab-pane>
        <el-tab-pane label="标识管理" name="identifier">
            <StaffIdentifier />
        </el-tab-pane>
        <el-tab-pane label="录像批量更新" name="batchupdate">
            <StaffBatchUpdateVideo />
        </el-tab-pane>
        <el-tab-pane label="后台日志" name="logs">
            <StaffLogs />
        </el-tab-pane>
    </el-tabs>
</template>

<script lang="ts" setup>
// 管理员操作接口，通过'/staff'访问
import { ElTabs, ElTabPane } from 'element-plus';
import { ref } from 'vue';
import StaffUserProfile from '@/components/staff/StaffUserProfile.vue';
import StaffVideoModel from '@/components/staff/StaffVideoModel.vue';
import StaffAccountLink from '@/components/staff/StaffAccountLink.vue';
import StaffIdentifier from '@/components/staff/StaffIdentifier.vue';
import StaffBatchUpdateVideo from '@/components/staff/StaffBatchUpdateVideo.vue';
import StaffLogs from '@/components/staff/StaffLogs.vue';

const activeTab = ref('userprofile');

</script>

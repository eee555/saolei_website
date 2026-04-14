<template>
    <el-tabs :model-value="activeTab" @tab-click="handleTabClick">
        <el-tab-pane v-for="tab in tabItems" :key="tab.name" :label="tab.label" :name="tab.name" />
        <router-view v-slot="{ Component }">
            <keep-alive>
                <component :is="Component" />
            </keep-alive>
        </router-view>
    </el-tabs>
</template>

<script lang="ts" setup>
import { ElTabPane, ElTabs } from 'element-plus';
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

const tabItems = [
    { name: 'userprofile', label: '用户信息' },
    { name: 'videomodel', label: '录像信息' },
    { name: 'accountlink', label: '账号绑定' },
    { name: 'identifier', label: '标识管理' },
    { name: 'batchupdate', label: '录像批量更新' },
    { name: 'logs', label: '后台日志' },
    { name: 'tournament', label: '比赛管理' },
    { name: 'task', label: '后台任务' },
] as const;
const validTabs = tabItems.map((item) => item.name);

// 根据当前路由路径计算激活的选项卡 name
const activeTab = computed(() => {
    const lastSegment = route.path.split('/').pop();
    return (validTabs as string[]).includes(lastSegment!) ? lastSegment! : 'userprofile';
});

// 点击选项卡时跳转到对应子路由
const handleTabClick = (tab: any) => {
    const tabName = tab.paneName;
    if (tabName) {
        router.replace(`${tabName}`);
    }
};
</script>

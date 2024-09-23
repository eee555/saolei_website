<template>
    <el-table :data="accountlinks">
        <el-table-column label="平台">
            <template #default="scope">
                <PlatformIcon :platform="scope.row.platform"/>
            </template>
        </el-table-column>
        <el-table-column label="ID">
            <template #default="scope">
                <el-link v-if="scope.row.platform == 'a'" :href="'https://minesweepergame.com/profile.php?pid=' + scope.row.identifier" target="_blank">{{ scope.row.identifier }}</el-link>
                <el-link v-else-if="scope.row.platform == 'c'" :href="'http://saolei.wang/Player/Index.asp?Id=' + scope.row.identifier" target="_blank">{{ scope.row.identifier }}</el-link>
                <el-link v-else-if="scope.row.platform == 'w'" :href="'https://minesweeper.online/player/' + scope.row.identifier" target="_blank">{{ scope.row.identifier }}</el-link>
                <el-text v-else>{{ scope.row.identifier }}</el-text>
            </template>
        </el-table-column>
        <el-table-column v-if="store.player.id==store.user.id" label="状态">
            <template #default="scope">
                <el-tooltip v-if="scope.row.verified" content="已验证">
                    <el-text type="success"><el-icon><CircleCheck/></el-icon></el-text>
                </el-tooltip>
                <el-tooltip v-else content="未验证，请联系管理员">
                    <el-text><el-icon><Clock/></el-icon></el-text>
                </el-tooltip>
            </template>
        </el-table-column>
        <el-table-column v-if="store.player.id==store.user.id" label="操作">
            <template #default="scope">
                <el-link :underline="false" @click.prevent="deleteRow(scope.$index)"><el-icon>
                        <Delete />
                    </el-icon></el-link>
            </template>
        </el-table-column>
    </el-table>
    <el-button v-if="store.player.id==store.user.id" style="width:100%" @click="formvisible = true">
        <el-icon>
            <Plus />
        </el-icon>
    </el-button>
    <el-dialog v-model="formvisible" title="添加关联账号" @closed="form.platform = ''; form.identifier = '';" width="500px">
        <el-form :model="form">
            <el-form-item label="平台">
                <el-select v-model="form.platform">
                    <el-option v-for="item in platformlist" :value="item.key" :label="item.name" />
                </el-select>
            </el-form-item>
            <el-form-item label="ID">
                <el-input v-model="form.identifier" maxlength="128" />
            </el-form-item>
            <el-form-item v-if="form.platform == 'c'">
                <el-text>
                    <b>如何找到ID</b><br />
                    登录<el-link href="http://saolei.wang" target="_blank" style="vertical-align: bottom;"
                        :underline="false">扫雷网</el-link>，进入“我的地盘”，ID位置如下图所示。<br />
                    <img src="../assets/IdGuideSaolei.png" width="100%" />
                </el-text>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" :disabled="!formValid"
                    @click.prevent="addLink(); formvisible = false;">确认</el-button>
                <el-button @click.prevent="formvisible = false">取消</el-button>
            </el-form-item>
        </el-form>
    </el-dialog>
</template>

<script setup lang="ts">

import { computed, onMounted, reactive, ref } from 'vue';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { useUserStore } from '@/store';
import { Action, ElMessageBox } from 'element-plus';
import { platformlist } from '@/utils/common/accountLinkPlatforms'
import PlatformIcon from './widgets/PlatformIcon.vue';

interface AccountLink {
    platform: string;
    identifier: string;
    verified: boolean;
}

const { proxy } = useCurrentInstance();
const store = useUserStore();
const accountlinks = ref<AccountLink[]>([]);
const formvisible = ref(false);
const form = reactive({
    platform: '',
    identifier: '',
})

const refresh = () => {
    proxy.$axios.get('accountlink/get/',
        {
            params: {
                id: store.user.id
            }
        }
    ).then(function (response) {
        accountlinks.value = response.data;
    })
}
onMounted(refresh)

const formValid = computed(() => {
    switch (form.platform) {
        case 'c':
            const num = parseInt(form.identifier, 10);
            return !isNaN(num) && num.toString() === form.identifier && num > 0
        default:
            return false;
    }
})

const addLink = () => {
    proxy.$axios.post('accountlink/add/',
        {
            platform: form.platform,
            identifier: form.identifier,
        }
    ).then(function (response) {
        refresh()
    })
}

const deleteRow = (index: number) => {
    ElMessageBox.confirm(accountlinks.value[index], '确认删除以下账号关联吗？').then(() => {
        proxy.$axios.post('accountlink/delete/', { platform: accountlinks.value[index].platform }).then(function (response) {
            refresh()
        })
    }).catch(() => { })
}

</script>
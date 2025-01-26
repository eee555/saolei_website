<template>
    <el-table :data="accountlinks" @expand-change="expandRow" :row-key="(row: any) => 'key' + row.platform">
        <el-table-column type="expand">
            <template #default="props">
                <el-text v-if="!props.row.verified" type="info" style="margin-left:50px" v-t="'accountlink.unverifiedText'"></el-text>
                <el-text v-else-if="props.row.data === undefined" type="info" style="margin-left:50px">No Data</el-text>
                <AccountSaolei v-else-if="props.row.platform == 'c'" :data="props.row.data" />
                <AccountMsgames v-else-if="props.row.platform == 'a'" :data="props.row.data" />
                <AccountWoM v-else-if="props.row.platform == 'w'" :data="props.row.data" />
            </template>
        </el-table-column>
        <el-table-column :label="t('accountlink.platform')">
            <template #default="scope">
                <PlatformIcon :platform="scope.row.platform" />
            </template>
        </el-table-column>
        <el-table-column label="ID">
            <template #default="scope">
                <!-- @vue-ignore -->
                <el-link :href="platformlist[scope.row.platform].profile(scope.row.identifier)" target="_blank">{{
                    scope.row.identifier }}</el-link>
            </template>
        </el-table-column>
        <el-table-column v-if="store.player.id == store.user.id || store.user.is_staff" :label="t('common.prop.status')">
            <template #default="scope">
                <el-tooltip v-if="scope.row.verified" :content="t('accountlink.verified')">
                    <el-text type="success"><el-icon>
                            <CircleCheck />
                        </el-icon></el-text>
                </el-tooltip>
                <el-tooltip v-else :content="t('accountlink.unverified')">
                    <el-text><el-icon>
                            <Clock />
                        </el-icon></el-text>
                </el-tooltip>
            </template>
        </el-table-column>
        <el-table-column v-if="store.player.id == store.user.id" :label="t('common.prop.action')">
            <template #default="scope">
                <el-link :underline="false" @click.prevent="deleteRow(scope.row)" type="danger"><el-icon>
                        <Delete />
                    </el-icon></el-link>
                &nbsp;
                <el-link v-if="scope.row.data !== undefined" :underline="false"
                    @click.prevent="updateRow(scope.row)"><el-icon>
                        <Refresh />
                    </el-icon></el-link>
            </template>
        </el-table-column>
    </el-table>
    <el-button v-if="store.player.id == store.user.id" style="width:100%" @click="formvisible = true" size="small">
        <el-icon>
            <Plus />
        </el-icon>
    </el-button>
    <el-dialog v-model="formvisible" :title="t('accountlink.addLink')"
        @closed="form.platform = ''; form.identifier = '';" width="500px">
        <el-form :model="form">
            <el-form-item :label="t('accountlink.platform')">
                <el-select v-model="form.platform">
                    <el-option v-for="(item, key) of platformlist" :value="key" :label="item.name"
                        :disabled="userHasPlatform(key)" />
                </el-select>
            </el-form-item>
            <el-form-item label="ID">
                <el-input v-model="form.identifier" maxlength="128" />
            </el-form-item>
            <el-form-item v-if="local.tooltip_show">
                <AccountLinkGuide :platform="form.platform" />
            </el-form-item>
            <el-form-item>
                <el-button type="primary" :disabled="!formValid" @click.prevent="addLink(); formvisible = false;">{{
                    t('common.button.confirm') }}</el-button>
                <el-button @click.prevent="formvisible = false">{{ t('common.button.cancel') }}</el-button>
            </el-form-item>
        </el-form>
    </el-dialog>
</template>

<script setup lang="ts">

import { computed, reactive, ref, watch } from 'vue';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { store, local } from '@/store';
import { ElNotification, ElDialog, ElForm, ElFormItem, ElInput, ElSelect, ElOption, ElLink, ElTable, ElTableColumn, ElText, ElTooltip, ElButton, ElIcon } from 'element-plus';
import { Platform, platformlist } from '@/utils/common/accountLinkPlatforms'
import PlatformIcon from './widgets/PlatformIcon.vue';
const AccountLinkGuide = () => import('./dialogs/AccountLinkGuide.vue')
const AccountSaolei = () => import('./accountlinks/AccountSaolei.vue');
const AccountMsgames = () => import('./accountlinks/AccountMsgames.vue');
const AccountWoM = () => import('./accountlinks/AccountWoM.vue');
import { useI18n } from 'vue-i18n';
import { httpErrorNotification } from './Notifications';
const { t } = useI18n();

interface AccountLink {
    platform: Platform;
    identifier: string;
    verified: boolean;
    data: any;
}

const { proxy } = useCurrentInstance();
const accountlinks = ref<AccountLink[]>([]);
const formvisible = ref(false);
const form = reactive({
    platform: '',
    identifier: '',
})

async function refresh() {
    if (store.player.id == 0) return;
    proxy.$axios.get('accountlink/get/',
        {
            params: {
                id: store.player.id
            }
        }
    ).then(function (response) {
        accountlinks.value = response.data;
    })
}
watch(() => store.player.id, refresh, { immediate: true })

const formValid = computed(() => {
    switch (form.platform) {
        case 'a':
        case 'c':
        case 'w':
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
    }).catch(httpErrorNotification)
}

const deleteRow = (row: any) => {
    // @ts-ignore
    ElMessageBox.confirm(t.t('accountlink.platform') + ' - ' + platformlist[row.platform].name + ', ID - ' + row.identifier, t.t('accountlink.deleteLinkMessage')).then(() => {
        proxy.$axios.post('accountlink/delete/', { platform: row.platform }).then(function (response) {
            refresh()
        })
    }).catch(httpErrorNotification)
}

const expandRow = (row: any) => {
    if (row.data !== undefined) return;
    if (row.verified === false) return;
    loadRow(row);
}

const updateRow = (row: any) => {
    proxy.$axios.post('accountlink/update/', { platform: row.platform }).then(function (response) {
        let data = response.data;
        if (data.type == 'success') loadRow(row);
        else if (data.type == 'error') {
            ElNotification({
                title: '更新失败',
                message: t('accountlink.updateError.' + data.category),
                type: 'error',
                duration: local.value.notification_duration,
            })
        }
    }).catch(httpErrorNotification)
}

const loadRow = (row: any) => {
    proxy.$axios.get('accountlink/get/',
        {
            params: { id: store.player.id, platform: row.platform }
        }
    ).then(function (response) {
        row.data = response.data
    }).catch(httpErrorNotification)
}

const userHasPlatform = (platform: string) => {
    for (let item of accountlinks.value) {
        if (item.platform == platform) return true;
    }
    return false;
}

</script>